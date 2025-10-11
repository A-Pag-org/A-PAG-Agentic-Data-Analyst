from __future__ import annotations

import json
import os
from io import BytesIO
import re
import difflib
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Tuple

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# LangChain / LangGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_experimental.agents.agent_toolkits.pandas.base import (
    create_pandas_dataframe_agent,
)
from langgraph.graph import StateGraph, END

# -------------------------
# Configuration & helpers
# -------------------------

APP_NAME = "AI Data Analysis & Visualization"
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
STORE_DIR = BASE_DIR / "stores"


def _get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    try:
        if key in st.secrets:  # type: ignore[attr-defined]
            value = st.secrets[key]
            if isinstance(value, (str, int, float)):
                return str(value)
            return default
    except Exception:
        pass
    return os.getenv(key, default)


def ensure_openai_key() -> str:
    api_key = _get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not set. Add it in Streamlit 'Secrets' or as an env var."
        )
    # Ensure LangChain/OpenAI clients see it
    os.environ.setdefault("OPENAI_API_KEY", api_key)
    return api_key


def ensure_dirs_for(user_id: str, dataset_id: str) -> Dict[str, Path]:
    data_path = DATA_DIR / user_id / f"{dataset_id}.csv"
    vector_dir = STORE_DIR / user_id / dataset_id
    data_path.parent.mkdir(parents=True, exist_ok=True)
    vector_dir.mkdir(parents=True, exist_ok=True)
    return {"data_path": data_path, "vector_dir": vector_dir}


# -------------------------
# Vector store (FAISS)
# -------------------------

def dataframe_to_documents(df: pd.DataFrame, max_rows: int = 20000, rows_per_chunk: int = 100) -> List[Document]:
    df_limited = df.head(max_rows)
    docs: List[Document] = []
    num_rows = len(df_limited)
    for start in range(0, num_rows, rows_per_chunk):
        end = min(start + rows_per_chunk, num_rows)
        chunk = df_limited.iloc[start:end]
        # Represent chunk as newline-delimited key=value pairs
        lines: List[str] = []
        for idx, row in chunk.iterrows():
            parts = [f"{col}={row[col]}" for col in chunk.columns]
            lines.append("; ".join(parts))
        content = "\n".join(lines)
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "row_start": int(start),
                    "row_end": int(end - 1),
                    "n_rows": int(end - start),
                },
            )
        )
    return docs


def build_vector_store(df: pd.DataFrame, vector_dir: Path, embedding_model: str = "text-embedding-3-small") -> None:
    embeddings = OpenAIEmbeddings(model=embedding_model)
    docs = dataframe_to_documents(df)
    store = FAISS.from_documents(docs, embeddings)
    store.save_local(str(vector_dir))


def load_vector_store(vector_dir: Path, embedding_model: str = "text-embedding-3-small") -> Optional[FAISS]:
    if not (vector_dir / "index.faiss").exists():
        return None
    embeddings = OpenAIEmbeddings(model=embedding_model)
    return FAISS.load_local(
        str(vector_dir), embeddings, allow_dangerous_deserialization=True
    )


def retrieve_context(vector_dir: Path, query: str, k: int = 5) -> List[Document]:
    store = load_vector_store(vector_dir)
    if store is None:
        return []
    return store.similarity_search(query, k=k)


# -------------------------
# LangGraph state & nodes
# -------------------------

class AppState(TypedDict, total=False):
    user_id: str
    dataset_id: str
    query: str
    prefer_visual: bool
    has_new_upload: bool
    top_k: int
    data_path: str
    vector_dir: str

    # Router outcome
    intent: str  # "ingest", "analyze", "visualize", or composite like "ingest_then_analyze"

    # Intermediate artifacts
    retrieved_text: str
    analysis_answer: str
    analysis_plan: Dict[str, Any]
    analysis_table: Dict[str, Any]
    analysis_logs: List[str]
    chart_spec: Dict[str, Any]
    final_answer: str


def get_llm() -> ChatOpenAI:
    ensure_openai_key()
    # Lightweight model suitable for routing/analysis
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


def router_node(state: AppState) -> AppState:
    """Route the query to an intent."""
    llm = get_llm()
    query = state.get("query", "").strip()
    has_new_upload = bool(state.get("has_new_upload"))
    prefer_visual = bool(state.get("prefer_visual"))

    classification_prompt = (
        "You are a router. Classify the user's intent for data tasks.\n"
        "Return one of: ingest, analyze, visualize, ingest_then_analyze, ingest_then_visualize.\n"
        "Rules: If a new file was uploaded, prefer ingest_then_* if a query exists, else ingest.\n"
        "If the query asks for plots/charts/visualization or the UI prefers visualization, choose visualize.\n"
        f"Query: {query!r}. PreferVisual: {prefer_visual}. HasNewUpload: {has_new_upload}."
    )
    intent = "analyze"
    try:
        completion = llm.invoke(classification_prompt)
        intent_raw = str(getattr(completion, "content", "")).lower()
        for candidate in [
            "ingest_then_visualize",
            "ingest_then_analyze",
            "ingest",
            "visualize",
            "analyze",
        ]:
            if candidate in intent_raw:
                intent = candidate
                break
        else:
            # Heuristic fallback if LLM returns free-form text
            if has_new_upload and query:
                intent = "ingest_then_analyze"
            elif has_new_upload:
                intent = "ingest"
            elif prefer_visual or any(k in query.lower() for k in ["plot", "chart", "graph", "visualiz", "show"]):
                intent = "visualize"
            else:
                intent = "analyze"
    except Exception:
        # Robust fallback
        if has_new_upload and query:
            intent = "ingest_then_analyze"
        elif has_new_upload:
            intent = "ingest"
        elif prefer_visual or any(k in query.lower() for k in ["plot", "chart", "graph", "visualiz", "show"]):
            intent = "visualize"
        else:
            intent = "analyze"

    state["intent"] = intent
    return state


def ingestion_agent(state: AppState) -> AppState:
    data_path = Path(state["data_path"])  # type: ignore[index]
    vector_dir = Path(state["vector_dir"])  # type: ignore[index]

    # Load dataframe and build vector store
    df = pd.read_csv(data_path)
    build_vector_store(df, vector_dir)

    # Decide next step (used by conditional edge)
    return state


def analysis_agent(state: AppState) -> AppState:
    data_path = Path(state["data_path"])  # type: ignore[index]
    vector_dir = Path(state["vector_dir"])  # type: ignore[index]
    query = state.get("query", "")
    k = int(state.get("top_k", 5))

    # Retrieve context from FAISS
    docs = retrieve_context(vector_dir, query, k=k)
    retrieved_text = "\n\n".join(d.page_content for d in docs) if docs else ""
    state["retrieved_text"] = retrieved_text

    # Attempt structured analysis plan first; fallback to pandas agent if needed
    df = pd.read_csv(data_path)
    llm = get_llm()

    try:
        plan = _generate_analysis_plan(llm, df, query)
        if plan and isinstance(plan, dict) and plan.get("steps"):
            result_df, logs = _execute_analysis_plan(df, plan)
            summary = _summarize_result(llm, result_df, query, logs)
            state["analysis_answer"] = summary
            # Store plan and a compact table for UI display
            state["analysis_plan"] = plan
            table_cols = [str(c) for c in result_df.columns.tolist()]
            table_rows = result_df.head(500).to_dict(orient="records")
            state["analysis_table"] = {"columns": table_cols, "rows": table_rows}
            state["analysis_logs"] = logs
            return state
    except Exception:
        # Fall back to pandas agent below
        pass

    # Fallback: Pandas agent over the DataFrame
    pandas_agent = create_pandas_dataframe_agent(llm, df, verbose=False, allow_dangerous_code=True)
    analysis_prompt = (
        "Use the DataFrame to answer the user's question succinctly.\n"
        "When helpful, perform aggregations, filters, or computations.\n"
        "If the question is ambiguous, state necessary assumptions briefly.\n"
        f"Question: {query}\n"
        f"Relevant rows (retrieved):\n{retrieved_text[:4000]}\n"
    )
    try:
        answer = pandas_agent.run(analysis_prompt)
    except Exception as exc:
        answer = f"Unable to run full analysis agent. Fallback summary: {df.describe(include='all').to_string()[:1500]}\nError: {exc}"

    state["analysis_answer"] = str(answer)
    return state


# -------------------------
# Structured analysis planning & execution
# -------------------------

def _generate_analysis_plan(llm: ChatOpenAI, df: pd.DataFrame, query: str) -> Dict[str, Any]:
    schema = {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "op": {
                            "type": "string",
                            "enum": [
                                "filter",
                                "select",
                                "groupby_agg",
                                "sort",
                                "topk",
                                "compute",
                                "rename",
                                "pivot",
                                "limit",
                                "dropna",
                                "fillna",
                                "cast",
                                "date_parse",
                                "date_trunc",
                                "window_rank",
                                "cumsum",
                                "pct_change",
                                "value_counts",
                                "dedupe",
                                "sample",
                            ],
                        },
                        "conditions": {"type": "array"},
                        "columns": {"type": "array"},
                        "column": {"type": "string"},
                        "by": {"type": "array"},
                        "aggregations": {"type": "array"},
                        "ascending": {"type": ["boolean", "array"]},
                        "k": {"type": "integer"},
                        "new_column": {"type": "string"},
                        "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                        "left": {"type": "object"},
                        "right": {"type": "object"},
                        "mapping": {"type": "object"},
                        "index": {"type": ["string", "array"]},
                        "values": {"type": ["string", "array"]},
                        "aggfunc": {"type": ["string", "array"]},
                        "fill_value": {},
                        "n": {"type": "integer"},
                        "subset": {"type": ["string", "array"]},
                        "how": {"type": "string", "enum": ["any", "all"]},
                        "value": {},
                        "types": {"type": "object"},
                        "freq": {"type": "string", "enum": ["day", "week", "month", "quarter", "year"]},
                        "partition_by": {"type": ["string", "array"]},
                        "rank_column": {"type": "string"},
                        "periods": {"type": "integer"},
                        "normalize": {"type": "boolean"},
                        "frac": {"type": "number"},
                        "random_state": {"type": ["integer", "null"]},
                    },
                    "required": ["op"],
                    "additionalProperties": True,
                },
            },
            "explain": {"type": "string"},
        },
        "required": ["steps"],
        "additionalProperties": True,
    }

    # Provide compact schema and metadata to the model
    dtypes_map = {str(c): str(t) for c, t in df.dtypes.items()}
    preview = df.head(10).to_dict(orient="records")
    prompt = (
        "You are a senior data analyst. Create a minimal JSON-only analysis plan\n"
        "to answer the user's question on the given DataFrame. Use only the schema below.\n"
        "Prefer simple, robust steps (filter, groupby_agg, sort, topk).\n"
        "JSON schema: \n"
        f"{json.dumps(schema)}\n"
        f"DataFrame columns and dtypes: {json.dumps(dtypes_map)}\n"
        f"Data preview (first 10 rows): {json.dumps(preview)[:4000]}\n"
        f"Question: {query}\n"
        "Return JSON only."
    )
    resp = llm.invoke(prompt)
    content = getattr(resp, "content", "{}")
    try:
        start = content.find("{")
        end = content.rfind("}")
        plan = json.loads(content[start : end + 1]) if start != -1 and end != -1 else {}
    except Exception:
        plan = {}
    return plan


def _resolve_column(df: pd.DataFrame, name: str) -> Optional[str]:
    if name in df.columns:
        return name
    # case-insensitive fallback
    lowered = {str(c).lower(): str(c) for c in df.columns}
    ci = lowered.get(str(name).lower())
    if ci:
        return ci
    # fuzzy match fallback
    candidates = [str(c) for c in df.columns]
    lowered_candidates = [c.lower() for c in candidates]
    import difflib as _difflib
    matches = _difflib.get_close_matches(str(name).lower(), lowered_candidates, n=1, cutoff=0.8)
    if matches:
        idx = lowered_candidates.index(matches[0])
        return candidates[idx]
    return None


def _as_number(value: Any) -> Any:
    try:
        if isinstance(value, (int, float)):
            return value
        text = str(value).strip()
        if text.lower() in {"true", "false"}:
            return text.lower() == "true"
        if text == "":
            return value
        return float(text) if ("." in text or "e" in text.lower()) else int(text)
    except Exception:
        return value


def _smart_coerce_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    # Try to coerce common numeric formats and dates
    for col in list(working.columns):
        series = working[col]
        if pd.api.types.is_object_dtype(series):
            # numeric-like strings: remove currency, commas, percent
            cleaned = series.astype(str).str.replace(r"[,$]", "", regex=True).str.replace("%", "", regex=False)
            coerced = pd.to_numeric(cleaned, errors="coerce")
            non_na_ratio = float(coerced.notna().mean()) if len(coerced) else 0.0
            if non_na_ratio > 0.6:
                working[col] = coerced
                continue
            # date-like by name
            import re as _re
            if _re.search(r"date|time|timestamp", str(col), flags=_re.I):
                try:
                    working[col] = pd.to_datetime(series, errors="coerce")
                except Exception:
                    pass
    return working


def _parse_dtype(name: str):
    t = str(name).lower()
    if t in {"int", "int64", "integer"}:
        return "int64"
    if t in {"float", "float64", "double"}:
        return "float64"
    if t in {"str", "string", "text"}:
        return "string"
    if t in {"bool", "boolean"}:
        return "boolean"
    if t in {"datetime", "timestamp", "date"}:
        return "datetime64[ns]"
    return None


def _date_trunc(series: pd.Series, freq: str) -> pd.Series:
    f = freq.lower()
    try:
        s = pd.to_datetime(series, errors="coerce")
        if f == "day":
            return s.dt.floor("D")
        if f == "week":
            return s.dt.to_period("W").apply(lambda p: p.start_time)
        if f == "month":
            return s.dt.to_period("M").dt.to_timestamp()
        if f == "quarter":
            return s.dt.to_period("Q").dt.to_timestamp()
        if f == "year":
            return s.dt.to_period("Y").dt.to_timestamp()
    except Exception:
        pass
    return series


def _execute_analysis_plan(df: pd.DataFrame, plan: Dict[str, Any]) -> Tuple[pd.DataFrame, List[str]]:
    working = _smart_coerce_dataframe(df)
    logs: List[str] = []

    def log(msg: str) -> None:
        logs.append(msg)

    steps: List[Dict[str, Any]] = list(plan.get("steps", []))
    for step in steps:
        op = str(step.get("op", "")).lower()
        if op == "filter":
            conditions = step.get("conditions") or []
            mask = pd.Series(True, index=working.index)
            for cond in conditions:
                col_raw = cond.get("column")
                optr = str(cond.get("operator", "==")).lower()
                val = cond.get("value")
                values = cond.get("values")
                ci = bool(cond.get("case_insensitive", True))
                col = _resolve_column(working, str(col_raw))
                if not col or col not in working.columns:
                    continue
                series = working[col]
                if optr in {"==", "!=", ">", ">=", "<", "<="}:
                    right = _as_number(val)
                    try:
                        expr_mask = getattr(series, "__{}__".format(
                            {"==": "eq", "!=": "ne", ">": "gt", ">=": "ge", "<": "lt", "<=": "le"}[optr]
                        ))(right)
                    except Exception:
                        expr_mask = series.astype(str).str.lower().eq(str(val).lower()) if ci else series.astype(str).eq(str(val))
                        if optr == "!=":
                            expr_mask = ~expr_mask
                elif optr in {"contains"}:
                    expr_mask = series.astype(str).str.contains(str(val), case=not ci, na=False)
                elif optr in {"in", "not_in"}:
                    vals = [ _as_number(v) for v in (values if isinstance(values, list) else [val]) ]
                    expr_mask = series.isin(vals)
                    if optr == "not_in":
                        expr_mask = ~expr_mask
                elif optr in {"between"}:
                    arr = values if isinstance(values, list) else [None, None]
                    left, right = (_as_number(arr[0]), _as_number(arr[1]))
                    expr_mask = series.between(left, right, inclusive="both")
                else:
                    continue
                mask &= expr_mask.fillna(False)
            working = working[mask]
            log(f"filter rows -> {len(working)} rows")

        elif op == "select":
            columns = [c for c in (step.get("columns") or []) if _resolve_column(working, str(c))]
            resolved = [_resolve_column(working, str(c)) for c in columns]
            resolved = [c for c in resolved if c is not None]
            if resolved:
                working = working.loc[:, resolved]  # type: ignore[index]
                log(f"select columns -> {resolved}")

        elif op == "compute":
            new_col = str(step.get("new_column") or "new")
            operation = str(step.get("operation") or "add").lower()
            left_spec = step.get("left") or {}
            right_spec = step.get("right") or {}
            left_col = _resolve_column(working, str(left_spec.get("column"))) if left_spec.get("column") else None
            right_col = _resolve_column(working, str(right_spec.get("column"))) if right_spec.get("column") else None
            left_val = working[left_col] if left_col else _as_number(left_spec.get("value"))
            right_val = working[right_col] if right_col else _as_number(right_spec.get("value"))
            try:
                if operation == "add":
                    working[new_col] = left_val + right_val  # type: ignore[operator]
                elif operation == "subtract":
                    working[new_col] = left_val - right_val  # type: ignore[operator]
                elif operation == "multiply":
                    working[new_col] = left_val * right_val  # type: ignore[operator]
                elif operation == "divide":
                    working[new_col] = left_val / right_val  # type: ignore[operator]
                log(f"compute {new_col} = {operation}(...)")
            except Exception:
                pass

        elif op == "groupby_agg":
            by = [c for c in (step.get("by") or []) if _resolve_column(working, str(c))]
            by_resolved = [_resolve_column(working, str(c)) for c in by]
            by_resolved = [c for c in by_resolved if c is not None]
            aggs_conf = step.get("aggregations") or []
            agg_map: Dict[str, List[str]] = {}
            for a in aggs_conf:
                col = _resolve_column(working, str(a.get("column")))
                func = str(a.get("agg", "sum")).lower()
                if col and func in {"sum", "mean", "count", "min", "max", "median"}:
                    agg_map.setdefault(col, []).append(func)
            if by_resolved and agg_map:
                grouped = working.groupby(by_resolved, dropna=False).agg(agg_map)
                # Flatten MultiIndex columns if present
                grouped.columns = ["_".join([str(c) for c in col]).strip("_") if isinstance(col, tuple) else str(col) for col in grouped.columns.values]
                working = grouped.reset_index()
                log(f"groupby {by_resolved} agg {agg_map}")

        elif op == "sort":
            by = [c for c in (step.get("by") or []) if _resolve_column(working, str(c))]
            by_resolved = [_resolve_column(working, str(c)) for c in by]
            by_resolved = [c for c in by_resolved if c is not None]
            ascending = step.get("ascending", False)
            try:
                working = working.sort_values(by=by_resolved or working.columns.tolist(), ascending=ascending)
                log(f"sort by {by_resolved or list(working.columns)} asc={ascending}")
            except Exception:
                pass

        elif op == "topk":
            k = int(step.get("k", 5))
            by = _resolve_column(working, str(step.get("by"))) if step.get("by") else None
            try:
                if by and pd.api.types.is_numeric_dtype(working[by]):
                    working = working.nlargest(k, by)
                else:
                    working = working.head(k)
                log(f"topk {k} by {by or 'head'}")
            except Exception:
                working = working.head(k)
                log(f"topk {k} (fallback head)")

        elif op == "rename":
            mapping = step.get("mapping") or {}
            safe_map = { (k if k in working.columns else _resolve_column(working, str(k))): str(v) for k, v in mapping.items() }
            safe_map = { k: v for k, v in safe_map.items() if k }
            if safe_map:
                working = working.rename(columns=safe_map)
                log(f"rename columns {safe_map}")

        elif op == "pivot":
            index = step.get("index")
            values = step.get("values")
            columns = step.get("columns")
            aggfunc = step.get("aggfunc", "sum")
            fill_value = step.get("fill_value")
            try:
                pivoted = pd.pivot_table(
                    working,
                    index=index,
                    columns=columns,
                    values=values,
                    aggfunc=aggfunc,
                    fill_value=fill_value,
                )
                if isinstance(pivoted.columns, pd.MultiIndex):
                    pivoted.columns = ["_".join([str(c) for c in col]).strip("_") for col in pivoted.columns]
                working = pivoted.reset_index()
                log("pivot table")
            except Exception:
                pass

        elif op == "limit":
            n = int(step.get("n", 10))
            working = working.head(n)
            log(f"limit {n}")

        elif op == "dropna":
            subset = step.get("subset")
            how = step.get("how", "any")
            try:
                working = working.dropna(subset=subset, how=how)
                log(f"dropna subset={subset} how={how}")
            except Exception:
                pass

        elif op == "fillna":
            value = step.get("value")
            try:
                if isinstance(value, dict):
                    working = working.fillna(value)
                else:
                    working = working.fillna(value)
                log("fillna applied")
            except Exception:
                pass

        elif op == "cast":
            types = step.get("types") or {}
            try:
                for k, v in list(types.items()):
                    col = _resolve_column(working, str(k))
                    if not col:
                        continue
                    target = _parse_dtype(v)
                    if target == "datetime64[ns]":
                        working[col] = pd.to_datetime(working[col], errors="coerce")
                    elif target:
                        working[col] = working[col].astype(target, errors="ignore")
                log(f"cast columns {types}")
            except Exception:
                pass

        elif op == "date_parse":
            columns = step.get("columns") or []
            for c in columns:
                col = _resolve_column(working, str(c))
                if col:
                    try:
                        working[col] = pd.to_datetime(working[col], errors="coerce")
                    except Exception:
                        pass
            log(f"date_parse {columns}")

        elif op == "date_trunc":
            column = _resolve_column(working, str(step.get("column"))) if step.get("column") else None
            freq = step.get("freq", "month")
            if column and column in working.columns:
                working[column] = _date_trunc(working[column], str(freq))
                log(f"date_trunc {column} freq={freq}")

        elif op == "window_rank":
            by = _resolve_column(working, str(step.get("by"))) if step.get("by") else None
            partition_by = step.get("partition_by")
            if isinstance(partition_by, str):
                partition_by = [partition_by]
            partition_resolved = [c for c in (partition_by or []) if _resolve_column(working, str(c))]
            partition_resolved = [ _resolve_column(working, str(c)) for c in partition_resolved ]
            partition_resolved = [ c for c in partition_resolved if c ]
            rank_col = str(step.get("rank_column") or "rank")
            ascending = bool(step.get("ascending", False))
            try:
                if by and by in working.columns:
                    if partition_resolved:
                        working[rank_col] = working.sort_values(by=by, ascending=ascending).groupby(partition_resolved)[by].rank(method="dense", ascending=ascending)
                    else:
                        working[rank_col] = working[by].rank(method="dense", ascending=ascending)
                    log(f"window_rank on {by} partition_by={partition_resolved}")
            except Exception:
                pass

        elif op == "cumsum":
            column = _resolve_column(working, str(step.get("column"))) if step.get("column") else None
            new_col = str(step.get("new_column") or f"{column}_cumsum")
            by = step.get("by")
            if isinstance(by, str):
                by = [by]
            by_resolved = [ _resolve_column(working, str(c)) for c in (by or []) ]
            by_resolved = [ c for c in by_resolved if c ]
            try:
                if column and by_resolved:
                    working[new_col] = working.groupby(by_resolved)[column].cumsum()
                elif column:
                    working[new_col] = working[column].cumsum()
                log(f"cumsum for {column} by={by_resolved}")
            except Exception:
                pass

        elif op == "pct_change":
            column = _resolve_column(working, str(step.get("column"))) if step.get("column") else None
            new_col = str(step.get("new_column") or f"{column}_pct_change")
            periods = int(step.get("periods", 1))
            by = step.get("by")
            if isinstance(by, str):
                by = [by]
            by_resolved = [ _resolve_column(working, str(c)) for c in (by or []) ]
            by_resolved = [ c for c in by_resolved if c ]
            try:
                if column and by_resolved:
                    working[new_col] = working.groupby(by_resolved)[column].pct_change(periods=periods)
                elif column:
                    working[new_col] = working[column].pct_change(periods=periods)
                log(f"pct_change for {column} by={by_resolved} periods={periods}")
            except Exception:
                pass

        elif op == "value_counts":
            column = _resolve_column(working, str(step.get("column"))) if step.get("column") else None
            normalize = bool(step.get("normalize", False))
            top = int(step.get("k", 20))
            if column and column in working.columns:
                vc = working[column].value_counts(normalize=normalize).head(top)
                working = vc.reset_index().rename(columns={"index": str(column), column: "count"})
                log(f"value_counts {column} normalize={normalize} top={top}")

        elif op == "dedupe":
            subset = step.get("subset")
            keep = step.get("keep", "first")
            try:
                working = working.drop_duplicates(subset=subset, keep=keep)
                log(f"dedupe subset={subset} keep={keep}")
            except Exception:
                pass

        elif op == "sample":
            n = step.get("n")
            frac = step.get("frac")
            random_state = step.get("random_state")
            try:
                if n is not None:
                    working = working.sample(n=int(n), random_state=random_state)
                elif frac is not None:
                    working = working.sample(frac=float(frac), random_state=random_state)
                log(f"sample n={n} frac={frac}")
            except Exception:
                pass

        else:
            # Unknown op: skip
            continue

    # Final compaction to avoid extremely wide outputs
    if len(working.columns) > 50:
        working = working.iloc[:, :50]
        log("trim columns to first 50 for display")

    return working, logs


def _summarize_result(llm: ChatOpenAI, df: pd.DataFrame, query: str, logs: List[str]) -> str:
    # Create a compact CSV preview for the model
    limited = df.head(30)
    csv_preview = limited.to_csv(index=False)
    prompt = (
        "You are a precise data analyst. Write a concise 2-4 sentence answer\n"
        "to the user's question based on the provided result table.\n"
        "Focus on key numbers, rankings, and trends.\n"
        f"Question: {query}\n"
        f"Applied steps: {json.dumps(logs)}\n"
        "Result CSV (first 30 rows):\n"
        f"{csv_preview[:6000]}\n"
    )
    try:
        resp = llm.invoke(prompt)
        content = getattr(resp, "content", "")
        return str(content).strip() or "Analysis complete. See the results table below."
    except Exception:
        try:
            return limited.describe(include='all').to_string()[:1200]
        except Exception:
            return "Analysis complete. See the results table below."


def _choose_chart_plan(llm: ChatOpenAI, df: pd.DataFrame, query: str) -> Dict[str, Any]:
    schema = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["bar", "line", "scatter", "histogram", "box"]},
            "x": {"type": "string"},
            "y": {"type": "string"},
            "color": {"type": "string"},
            "title": {"type": "string"},
            "aggregation": {"type": "string", "enum": ["sum", "mean", "count", "median", "min", "max"]},
        },
        "required": ["type"],
        "additionalProperties": True,
    }
    cols = ", ".join([str(c) for c in df.columns.tolist()])
    prompt = (
        "Decide an appropriate chart plan for the question using the given columns.\n"
        "Return a compact JSON object only, matching this JSON schema: \n"
        f"{json.dumps(schema)}\n"
        f"Columns: {cols}\n"
        f"Question: {query}\n"
    )
    resp = llm.invoke(prompt)
    content = getattr(resp, "content", "{}")
    try:
        # Try to extract JSON directly
        start = content.find("{")
        end = content.rfind("}")
        plan = json.loads(content[start : end + 1]) if start != -1 and end != -1 else {}
    except Exception:
        plan = {"type": "bar"}
    return plan


def _render_plotly_from_plan(df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
    chart_type = str(plan.get("type", "bar")).lower()
    x = plan.get("x")
    y = plan.get("y")
    color = plan.get("color")
    title = plan.get("title") or ""
    # Fallbacks to keep charts robust
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()
    if y is None:
        y = numeric_cols[0] if numeric_cols else (all_cols[0] if all_cols else None)
    if x is None:
        x_candidates = [c for c in all_cols if c != y]
        x = x_candidates[0] if x_candidates else (all_cols[0] if all_cols else None)

    if chart_type == "line":
        fig = px.line(df, x=x, y=y, color=color, title=title)
    elif chart_type == "scatter":
        # Ensure we have two numeric axes for scatter if possible
        if len(numeric_cols) >= 2:
            if x not in numeric_cols:
                x = numeric_cols[0]
            if y not in numeric_cols or y == x:
                y = numeric_cols[1]
        fig = px.scatter(df, x=x, y=y, color=color, title=title)
    elif chart_type == "histogram":
        fig = px.histogram(df, x=x or y, color=color, title=title)
    elif chart_type == "box":
        fig = px.box(df, x=color or x, y=y, title=title)
    else:
        fig = px.bar(df, x=x, y=y, color=color, title=title)

    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig


def visualization_agent(state: AppState) -> AppState:
    data_path = Path(state["data_path"])  # type: ignore[index]
    query = state.get("query", "")

    df = pd.read_csv(data_path)
    llm = get_llm()
    plan = _choose_chart_plan(llm, df, query)
    fig = _render_plotly_from_plan(df, plan)

    state["chart_spec"] = fig.to_dict()
    # Provide a concise caption
    state["analysis_answer"] = state.get("analysis_answer") or "Suggested visualization shown below."
    return state


def finalize_node(state: AppState) -> AppState:
    # Prefer analysis answer; otherwise generic message
    answer = state.get("analysis_answer") or "Task completed."
    state["final_answer"] = str(answer)
    return state


# Graph wiring

def _route_from_router(state: AppState) -> str:
    intent = state.get("intent", "analyze")
    mapping = {
        "ingest": "ingestion",
        "analyze": "analysis",
        "visualize": "visualization",
        "ingest_then_analyze": "ingestion",
        "ingest_then_visualize": "ingestion",
    }
    return mapping.get(intent, "analysis")


def _route_after_ingest(state: AppState) -> str:
    intent = state.get("intent", "analyze")
    if intent == "ingest_then_visualize":
        return "visualization"
    if intent in ("ingest_then_analyze",):
        return "analysis"
    # No follow-up intent
    return "finalize"


def build_graph() -> Any:
    graph = StateGraph(AppState)
    graph.add_node("router", router_node)
    graph.add_node("ingestion", ingestion_agent)
    graph.add_node("analysis", analysis_agent)
    graph.add_node("visualization", visualization_agent)
    graph.add_node("finalize", finalize_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        _route_from_router,
        {"ingestion": "ingestion", "analysis": "analysis", "visualization": "visualization"},
    )

    graph.add_conditional_edges(
        "ingestion",
        _route_after_ingest,
        {"analysis": "analysis", "visualization": "visualization", "finalize": "finalize"},
    )

    # Default transitions to finalize
    graph.add_edge("analysis", "finalize")
    graph.add_edge("visualization", "finalize")

    return graph.compile()


# -------------------------
# UI
# -------------------------

st.set_page_config(page_title=APP_NAME, layout="wide")

# Inject custom JavaScript to suppress known Streamlit console warnings
# These warnings are from Streamlit's internal implementation and don't affect functionality
import streamlit.components.v1 as components

components.html("""
<script>
// Suppress specific console warnings that come from Streamlit's internal JavaScript
(function() {
    const originalWarn = console.warn;
    const originalError = console.error;
    
    const suppressedPatterns = [
        /Unrecognized feature.*ambient-light-sensor/i,
        /Unrecognized feature.*battery/i,
        /Unrecognized feature.*document-domain/i,
        /Unrecognized feature.*layout-animations/i,
        /Unrecognized feature.*legacy-image-formats/i,
        /Unrecognized feature.*oversized-images/i,
        /Unrecognized feature.*vr/i,
        /Unrecognized feature.*wake-lock/i,
        /allow-scripts.*allow-same-origin.*sandbox/i
    ];
    
    console.warn = function(...args) {
        const message = args.join(' ');
        if (!suppressedPatterns.some(pattern => pattern.test(message))) {
            originalWarn.apply(console, args);
        }
    };
    
    console.error = function(...args) {
        const message = args.join(' ');
        if (!suppressedPatterns.some(pattern => pattern.test(message))) {
            originalError.apply(console, args);
        }
    };
})();
</script>
""", height=0)

# Automatically retrieve and set the OpenAI API key from Streamlit secrets
try:
    ensure_openai_key()
except RuntimeError as e:
    st.error(str(e))
    st.info("Please add your OPENAI_API_KEY to Streamlit secrets or as an environment variable.")
    st.stop()

st.title(APP_NAME)

with st.sidebar:
    st.header("Settings")
    user_id = st.text_input("User ID", value=st.session_state.get("user_id", "user"))
    dataset_id = st.text_input("Dataset ID", value=st.session_state.get("dataset_id", "dataset"))
    prefer_visual = st.checkbox("Prefer visualization", value=False, help="Hints the router towards charts.")
    top_k = st.slider("Retriever top_k", min_value=3, max_value=15, value=5, step=1)

    clear_btn = st.button("Clear vector store", type="primary")

# Manage paths
paths = ensure_dirs_for(user_id, dataset_id)
data_path: Path = paths["data_path"]  # type: ignore[assignment]
vector_dir: Path = paths["vector_dir"]  # type: ignore[assignment]

if clear_btn:
    # Remove FAISS files if present
    for p in [vector_dir / "index.faiss", vector_dir / "index.pkl"]:
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass
    st.success("Vector store cleared.")

st.markdown("Upload a file and/or ask a question. The router will decide what to do.")

col_left, col_right = st.columns([2, 3])

with col_left:
    uploaded = st.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "xls", "json"])
    has_new_upload = False
    if uploaded is not None:
        try:
            raw = uploaded.getvalue()
            name = (uploaded.name or "").lower()
            if name.endswith(".csv"):
                df = pd.read_csv(BytesIO(raw))
            elif name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(BytesIO(raw))
            elif name.endswith(".json"):
                try:
                    df = pd.read_json(BytesIO(raw))
                except ValueError:
                    df = pd.read_json(BytesIO(raw), lines=True)
            else:
                df = pd.read_csv(BytesIO(raw))
            df.to_csv(data_path, index=False)
            has_new_upload = True
            st.success(f"File saved to {data_path}")
            st.caption(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
            st.dataframe(df.head(20), use_container_width=True)
        except Exception as exc:
            st.error(f"Failed to read file: {exc}")

with col_right:
    default_q = "What are the top 5 products by revenue?"
    query = st.text_area("Your query", value=default_q, height=120)
    run = st.button("Run", type="primary")

if run:
    try:
        # Pre-flight checks
        if not data_path.exists():
            st.warning("No dataset found. Please upload a file first.")
        # Build and run graph
        app = build_graph()
        initial_state: AppState = {
            "user_id": user_id,
            "dataset_id": dataset_id,
            "query": query,
            "prefer_visual": prefer_visual,
            "has_new_upload": bool(has_new_upload),
            "top_k": int(top_k),
            "data_path": str(data_path),
            "vector_dir": str(vector_dir),
        }

        # Execute graph
        result: AppState = app.invoke(initial_state)  # type: ignore[assignment]

        # Present results
        answer = result.get("final_answer") or ""
        st.markdown("**Answer**")
        st.write(answer)

        # Show chart if present
        chart_spec = result.get("chart_spec")
        if isinstance(chart_spec, dict) and chart_spec:
            try:
                fig = go.Figure(chart_spec)
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.caption("Chart JSON (failed to render):")
                st.code(json.dumps(chart_spec, indent=2))

        # Show tabular results if present
        analysis_table = result.get("analysis_table")
        if isinstance(analysis_table, dict) and analysis_table.get("rows"):
            try:
                table_df = pd.DataFrame(analysis_table.get("rows", []))
                cols = analysis_table.get("columns")
                if isinstance(cols, list) and cols:
                    ordered = [c for c in cols if c in table_df.columns]
                    if ordered:
                        table_df = table_df.loc[:, ordered]
                st.markdown("**Results table**")
                st.dataframe(table_df, use_container_width=True)
            except Exception:
                st.caption("Results table (raw):")
                st.code(json.dumps(analysis_table)[:8000])

        # Optional: show retrieved snippets
        retrieved_text = result.get("retrieved_text")
        if retrieved_text:
            with st.expander("Retrieved context", expanded=False):
                st.code(retrieved_text[:8000])

        # Show analysis logs if present
        analysis_logs = result.get("analysis_logs")
        if isinstance(analysis_logs, list) and analysis_logs:
            with st.expander("Analysis steps", expanded=False):
                st.code("\n".join(str(x) for x in analysis_logs))

    except Exception as exc:
        st.error(f"Run failed: {exc}")

# Footer note removed per request
