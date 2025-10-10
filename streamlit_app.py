from __future__ import annotations

import json
import os
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

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

    # Pandas agent over the DataFrame
    df = pd.read_csv(data_path)
    llm = get_llm()
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
        ensure_openai_key()
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

        # Optional: show retrieved snippets
        retrieved_text = result.get("retrieved_text")
        if retrieved_text:
            with st.expander("Retrieved context", expanded=False):
                st.code(retrieved_text[:8000])

    except Exception as exc:
        st.error(f"Run failed: {exc}")

# Footer note
st.caption(
    "Tip: Set your OPENAI_API_KEY in Streamlit Secrets for Streamlit Community Cloud deployment."
)
