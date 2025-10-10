# Streamlit AI Data Analysis & Visualization

Single-repo Streamlit app that ingests a user-uploaded file, routes the user's natural language query with a LangGraph router, dynamically executes agents (ingestion, analysis, visualization), retrieves data via FAISS, and renders responses including Plotly charts.

## One-click deploy (Streamlit Community Cloud)

1) Push this repo to GitHub.
2) Create a new Streamlit Community Cloud app pointing to this repo.
3) Set Secrets → add `OPENAI_API_KEY`.
4) Save and run. No other manual steps are required.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Set your key:

```bash
export OPENAI_API_KEY=sk-...
```

Alternatively, in Streamlit Community Cloud, set it under Secrets → `OPENAI_API_KEY`.

## What it does

- User uploads a file and types a query.
- LangGraph router infers intent: analyze, visualize, ingest, or chained ingest→(analyze/visualize).
- Ingestion agent parses the file into a DataFrame and builds a FAISS vector store with OpenAI embeddings.
- Analysis agent retrieves similar chunks from FAISS and uses a Pandas agent to answer.
- Visualization agent determines a suitable chart plan and returns a Plotly figure JSON.
- App displays LLM text answer and renders Plotly charts.

## Notes

- Only `OPENAI_API_KEY` is required to run in the cloud.
- Vector store is saved under `stores/<user_id>/<dataset_id>/` and can be cleared from the sidebar.
