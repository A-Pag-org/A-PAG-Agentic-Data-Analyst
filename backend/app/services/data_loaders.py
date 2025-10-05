from __future__ import annotations

import io
from typing import List, Optional

import pandas as pd
from fastapi import UploadFile
from llama_index.core import Document

from .supabase_client import get_supabase_service_client


def dataframe_to_documents(df: pd.DataFrame, filename: Optional[str] = None) -> List[Document]:
    safe_df = df.fillna("").astype(str)
    records = safe_df.to_dict(orient="records")

    documents: List[Document] = []
    for row_index, record in enumerate(records):
        text = " | ".join(f"{key}: {value}" for key, value in record.items())
        metadata = {
            "row_index": row_index,
            "filename": filename or "",
            "columns": list(safe_df.columns),
        }
        documents.append(Document(text=text, metadata=metadata))
    return documents


async def uploadfile_to_dataframe(file: UploadFile) -> pd.DataFrame:
    content: bytes = await file.read()
    filename = (file.filename or "").lower()
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        return pd.read_excel(io.BytesIO(content))
    try:
        return pd.read_csv(io.BytesIO(content))
    except UnicodeDecodeError:
        return pd.read_csv(io.BytesIO(content), encoding="latin-1")


async def uploadfile_to_documents(file: UploadFile) -> List[Document]:
    df = await uploadfile_to_dataframe(file)
    return dataframe_to_documents(df, filename=file.filename)


def load_user_documents_from_supabase(user_id: str, limit: Optional[int] = None) -> List[Document]:
    """Load documents for BM25 etc. Each row becomes a Document.

    Reads from existing tables `original_data` and `data_chunks` scoped by user.
    """
    supabase = get_supabase_service_client()

    # Get all original_data ids for user
    orig_resp = (
        supabase.table("original_data")
        .select("id")
        .eq("user_id", user_id)
        .execute()
    )
    ids = [row["id"] for row in getattr(orig_resp, "data", [])]
    if not ids:
        return []

    # Fetch chunks
    query = (
        supabase.table("data_chunks")
        .select("content,metadata,original_data_id,chunk_index")
        .in_("original_data_id", ids)
        .order("created_at", desc=True)
    )
    if limit:
        query = query.limit(limit)
    chunks_resp = query.execute()

    documents: List[Document] = []
    for row in getattr(chunks_resp, "data", []) or []:
        metadata = row.get("metadata") or {}
        metadata.update(
            {
                "original_data_id": row.get("original_data_id"),
                "chunk_index": row.get("chunk_index"),
            }
        )
        documents.append(Document(text=row.get("content", ""), metadata=metadata))
    return documents
