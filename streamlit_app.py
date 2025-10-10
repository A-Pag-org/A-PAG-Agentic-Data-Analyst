from __future__ import annotations

import base64
import json
import os
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.exceptions import (
    RequestException,
    ConnectionError as RequestsConnectionError,
    HTTPError,
)
import streamlit as st


# -------------------------
# Configuration helpers
# -------------------------

def _get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    try:
        # streamlit secrets (preferred on Streamlit Cloud)
        if key in st.secrets:
            value = st.secrets[key]
            if isinstance(value, (str, int, float)):
                return str(value)
            return default
    except Exception:
        pass
    return os.getenv(key, default)


def normalize_base_url(raw_value: Optional[str]) -> str:
    """Return a normalized base URL with a scheme and no trailing slash.

    - Adds https:// when missing (http:// for localhost/127.0.0.1/0.0.0.0 or when a port is present)
    - Falls back to http://localhost:8000 when empty
    - Strips surrounding whitespace and trailing slashes
    """
    value = (raw_value or "").strip()
    if not value:
        return "http://localhost:8000"
    if value.startswith(("http://", "https://")):
        normalized = value
    elif value.startswith("//"):
        normalized = f"https:{value}"
    else:
        is_local_like = value.startswith(("localhost", "127.0.0.1", "0.0.0.0"))
        has_port = ":" in value and not value.startswith("http")
        default_scheme = "http://" if (is_local_like or has_port) else "https://"
        normalized = f"{default_scheme}{value}"
    return normalized.rstrip("/")


def get_backend_config() -> Tuple[str, Optional[str]]:
    # Prefer session state, then env/secrets in this order: BACKEND_URL, NEXT_PUBLIC_BACKEND_URL
    detected_backend_raw = (
        st.session_state.get("backend_url")
        or _get_secret("BACKEND_URL", None)
        or _get_secret("NEXT_PUBLIC_BACKEND_URL", None)
        or "http://localhost:8000"
    )
    detected_backend = normalize_base_url(str(detected_backend_raw))
    auth_token = st.session_state.get(
        "auth_bearer_token",
        _get_secret("AUTH_BEARER_TOKEN", None),
    )
    return detected_backend, auth_token


# -------------------------
# Backend client
# -------------------------

class BackendClient:
    def __init__(self, base_url: str, bearer_token: Optional[str] = None):
        # Guard against invalid base URLs without scheme
        normalized = normalize_base_url(base_url)
        if "://" not in normalized:
            raise ValueError("Invalid base_url: missing URL scheme (http:// or https://)")
        self.base_url = normalized.rstrip("/")
        self.bearer_token = bearer_token

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        return headers

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = requests.get(url, params=params, headers=self._headers(), timeout=60)
        resp.raise_for_status()
        return resp.json()

    def post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = requests.post(url, json=payload, headers=self._headers(), timeout=120)
        resp.raise_for_status()
        return resp.json()

    def post_multipart(
        self,
        path: str,
        files: Dict[str, Tuple[str, bytes, str]],
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = requests.post(url, files=files, data=data or {}, headers=self._headers(), timeout=300)
        resp.raise_for_status()
        return resp.json()


# -------------------------
# UI helpers
# -------------------------

def show_sources(sources: List[Dict[str, Any]]) -> None:
    if not sources:
        st.info("No sources returned.")
        return
    for idx, node in enumerate(sources, start=1):
        with st.expander(f"Source {idx} (score={node.get('score')})", expanded=False):
            text = node.get("text")
            if text:
                st.write(text)
            meta = node.get("metadata")
            if isinstance(meta, dict) and meta:
                st.json(meta)


def show_visualization(spec: Optional[Dict[str, Any]]) -> None:
    if not isinstance(spec, dict):
        st.info("No visualization available.")
        return
    # If the spec contains embedded data, we can render directly.
    # Otherwise, display raw spec for inspection.
    try:
        st.vega_lite_chart(spec=spec, use_container_width=True)
    except Exception:
        st.caption("Vega-Lite spec (rendering failed; showing raw spec):")
        st.code(json.dumps(spec, indent=2))


def show_forecast_plots(plot_png_b64: Optional[str], components_png_b64: Optional[str]) -> None:
    cols = st.columns(2)
    if plot_png_b64:
        with cols[0]:
            st.image(base64.b64decode(plot_png_b64), caption="Forecast")
    if components_png_b64:
        with cols[1]:
            st.image(base64.b64decode(components_png_b64), caption="Components")


# -------------------------
# App layout
# -------------------------

st.set_page_config(page_title="AI Analytics (Streamlit)", layout="wide")

st.title("AI Data Analytics Platform — Streamlit UI")

# Sidebar configuration
with st.sidebar:
    st.header("Backend Settings")
    default_backend, default_token = get_backend_config()
    backend_url = st.text_input("Backend URL", value=default_backend, placeholder="https://your-backend.example.com")
    auth_bearer_token = st.text_input("Auth Bearer Token", value=default_token or "", type="password")
    user_id = st.text_input("User ID", value=st.session_state.get("user_id", "streamlit_user"))

    # Persist to session state
    st.session_state["backend_url"] = backend_url
    st.session_state["auth_bearer_token"] = auth_bearer_token or None
    st.session_state["user_id"] = user_id

    client = BackendClient(backend_url, bearer_token=(auth_bearer_token or None))

    # Simple connectivity check (health endpoint is public)
    if st.button("Test Connection"):
        try:
            health = client.get("/api/v1/health")
            st.success(f"Health: {health}")
        except Exception as exc:
            st.error(f"Connection failed: {exc}")

# Maintain conversation session id across runs
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None


# Tabs for main flows
upload_tab, ask_tab, search_tab, forecast_tab = st.tabs(["Upload", "Ask", "Search", "Forecast"]) 


with upload_tab:
    st.subheader("Upload Data")
    st.caption("Supported: CSV, Excel (xlsx), JSON")
    uploaded = st.file_uploader("Choose a file", type=["csv", "xlsx", "json"]) 
    dataset_id = st.text_input("Dataset ID (optional)", value="")
    if st.button("Upload", disabled=(uploaded is None)):
        if uploaded is None:
            st.warning("Please select a file first.")
        else:
            try:
                # Quick reachability check before attempting upload
                try:
                    client.get("/api/v1/health")
                except Exception as health_exc:
                    st.error(
                        f"Backend not reachable at '{backend_url}'. "
                        f"Update 'Backend URL' in the sidebar or start the backend. Details: {health_exc}"
                    )
                    raise

                file_bytes = uploaded.getvalue()
                content_type = uploaded.type or "application/octet-stream"
                files = {
                    "file": (uploaded.name, file_bytes, content_type),
                }
                data = {
                    "user_id": user_id,
                }
                if dataset_id.strip():
                    data["dataset_id"] = dataset_id.strip()
                result = client.post_multipart("/api/v1/ingest/upload", files=files, data=data)
                st.success("Upload succeeded.")
                st.json(result)
            except RequestsConnectionError as exc:
                st.error(
                    f"Upload failed: cannot connect to backend at '{backend_url}'. "
                    f"Ensure the backend is running and the URL is correct. Details: {exc}"
                )
            except HTTPError as exc:
                status = getattr(exc.response, "status_code", "")
                detail: Any = None
                if getattr(exc, "response", None) is not None:
                    try:
                        detail = exc.response.json()
                    except Exception:
                        try:
                            detail = exc.response.text
                        except Exception:
                            detail = None
                st.error(
                    f"Upload failed: HTTP {status} {detail if detail else ''}".strip()
                )
            except RequestException as exc:
                st.error(f"Upload failed due to network error: {exc}")
            except Exception as exc:
                st.error(f"Upload failed: {exc}")


with ask_tab:
    st.subheader("Ask a Question")
    question = st.text_area("Your question", value="What are the top 5 products by revenue?", height=80)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        visualize = st.checkbox("Suggest visualization", value=True)
    with col_b:
        forecast_flag = st.checkbox("Suggest forecast", value=False)
    with col_c:
        keep_history = st.checkbox("Keep conversation history", value=True)

    if st.button("Analyze"):
        try:
            payload = {
                "user_id": user_id,
                "query": question,
                "visualize": bool(visualize),
                "forecast": bool(forecast_flag),
                "session_id": st.session_state.get("session_id") if keep_history else None,
            }
            resp = client.post_json("/api/v1/agents/analyze", payload)

            # Persist session id if provided
            maybe_session_id = resp.get("session_id") or resp.get("data", {}).get("session_id")
            if maybe_session_id:
                st.session_state["session_id"] = maybe_session_id

            st.markdown(f"**Answer:** {resp.get('answer','')}")
            explanation = resp.get("explanation")
            if explanation:
                st.markdown("**Explanation:**")
                st.write(explanation)

            viz_spec = resp.get("visualization_spec")
            if viz_spec:
                st.markdown("**Suggested Visualization:**")
                show_visualization(viz_spec)

            sources = resp.get("sources") or []
            st.markdown("**Sources:**")
            show_sources(sources)
        except Exception as exc:
            st.error(f"Analyze failed: {exc}")


with search_tab:
    st.subheader("Semantic Search")
    q = st.text_input("Query", value="sales trend over last year")
    n_cols = st.columns(2)
    with n_cols[0]:
        if st.button("Search"):
            try:
                params = {"user_id": user_id, "q": q}
                result = client.get("/api/v1/search/query", params=params)
                st.markdown(f"**Answer:** {result.get('answer','')}")
                st.markdown("**Sources:**")
                show_sources(result.get("source_nodes") or [])
            except Exception as exc:
                st.error(f"Search failed: {exc}")


with forecast_tab:
    st.subheader("Forecast from File or JSON")
    mode = st.radio("Input Mode", options=["From File", "From JSON"], horizontal=True)

    if mode == "From File":
        f = st.file_uploader("Upload timeseries file", type=["csv", "xlsx", "json"], key="forecast_file")
        target_column = st.text_input("Target column (numeric)", value="y")
        date_column = st.text_input("Date column (optional)", value="")
        periods = st.number_input("Periods", min_value=1, max_value=3650, value=30)
        freq = st.selectbox("Frequency", ["D", "W", "M", "Q", "Y"], index=0)
        if st.button("Run Forecast", disabled=f is None):
            if f is None:
                st.warning("Please upload a file.")
            else:
                try:
                    file_bytes = f.getvalue()
                    files = {"file": (f.name, file_bytes, f.type or "application/octet-stream")}
                    data = {
                        "target_column": target_column,
                        "periods": int(periods),
                        "freq": freq,
                    }
                    if date_column.strip():
                        data["date_column"] = date_column.strip()
                    result = client.post_multipart("/api/v1/forecast/from-file", files=files, data=data)

                    st.success("Forecast generated.")
                    meta = result.get("metadata") or {}
                    st.json(meta)
                    st.markdown("**Metrics:**")
                    st.json(result.get("metrics") or {})
                    st.markdown("**History sample:**")
                    st.write((result.get("history") or [])[:10])
                    st.markdown("**Forecast sample:**")
                    st.write((result.get("forecast") or [])[:10])

                    show_forecast_plots(result.get("plot_png_base64"), result.get("components_png_base64"))
                except Exception as exc:
                    st.error(f"Forecast failed: {exc}")
    else:
        st.caption("Paste JSON array of rows with date and target columns.")
        sample_json = [
            {"ds": "2024-01-01", "y": 100},
            {"ds": "2024-01-02", "y": 120},
            {"ds": "2024-01-03", "y": 115},
        ]
        raw = st.text_area("Rows (JSON)", value=json.dumps(sample_json, indent=2), height=180)
        target_column = st.text_input("Target column (numeric)", value="y", key="json_target")
        date_column = st.text_input("Date column (optional)", value="ds", key="json_date")
        periods = st.number_input("Periods", min_value=1, max_value=3650, value=30, key="json_periods")
        freq = st.selectbox("Frequency", ["D", "W", "M", "Q", "Y"], index=0, key="json_freq")
        if st.button("Run Forecast (JSON)"):
            try:
                rows = json.loads(raw)
                payload = {
                    "data": rows,
                    "target_column": target_column,
                    "date_column": date_column or None,
                    "periods": int(periods),
                    "freq": str(freq),
                }
                result = client.post_json("/api/v1/forecast/from-json", payload)
                st.success("Forecast generated.")
                meta = result.get("metadata") or {}
                st.json(meta)
                st.markdown("**Metrics:**")
                st.json(result.get("metrics") or {})
                st.markdown("**History sample:**")
                st.write((result.get("history") or [])[:10])
                st.markdown("**Forecast sample:**")
                st.write((result.get("forecast") or [])[:10])
                show_forecast_plots(result.get("plot_png_base64"), result.get("components_png_base64"))
            except Exception as exc:
                st.error(f"Forecast failed: {exc}")
