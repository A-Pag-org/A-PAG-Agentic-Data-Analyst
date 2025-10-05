from __future__ import annotations

import io
import os
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from fastapi import UploadFile
from openai import OpenAI
from .chromadb_client import (
    get_or_create_collection_for,
    add_or_update_documents,
    autosave_collection_to_supabase,
)

from .supabase_client import get_supabase_service_client
from ..core.config import settings

# LlamaIndex (for constructing documents; embeddings via OpenAI client for control)
from llama_index.core import Document, VectorStoreIndex

# LlamaIndex integration utilities
from .text_splitters import split_documents_to_texts_and_metas
from .embeddings_cache import embed_with_cache, EmbeddingCache
from .vector_store_pg import build_or_update_vector_index


class DataProcessor:
    def __init__(self, chroma_persist_dir: Optional[str] = None):
        # Backward-compat arg preserved; persistence is now controlled via config
        if chroma_persist_dir:
            os.makedirs(chroma_persist_dir, exist_ok=True)
        self.embedding_model_name: str = settings.embedding_model or "text-embedding-3-large"
        self.openai_client = OpenAI(api_key=settings.openai_api_key)

    async def process_upload(self, file: UploadFile, user_id: str, dataset_id: Optional[str] = None) -> Dict[str, Any]:
        # 1. Parse file (CSV/Excel)
        df, file_bytes, content_type = await self.parse_file(file)

        # 2. Create LlamaIndex documents (row-per-document)
        documents, base_texts, base_metadatas = self.create_documents(df, filename=file.filename)

        # 3. Split into semantic/sentence chunks and embed with cache
        texts, metadatas = split_documents_to_texts_and_metas(documents)
        embeddings = self.generate_embeddings(texts)

        # Optionally build an in-memory index (useful for local queries)
        _ = VectorStoreIndex.from_documents([Document(text=t, metadata=m) for t, m in zip(texts, metadatas)])

        # 4. Store in Supabase pgvector (and metadata about original file)
        original_data_id = self.store_in_supabase(
            user_id=user_id,
            filename=file.filename,
            file_size=len(file_bytes),
            df=df,
            texts=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        # 5. Index into Postgres pgvector via LlamaIndex store (for hybrid retrieval)
        try:
            self.index_into_pgvector(texts=texts, metadatas=metadatas)
        except Exception:
            # Don't fail the whole request if vector indexing fails; storage in Supabase succeeded
            pass

        # 6. Create / update ChromaDB collection (optional legacy hybrid)
        collection_name = self.upsert_into_chroma(
            user_id=user_id,
            dataset_id=dataset_id,
            original_data_id=original_data_id,
            texts=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        return {
            "status": "success",
            "document_count": len(documents),
            "rows": len(texts),
            "original_data_id": original_data_id,
            "chroma_collection": collection_name,
        }

    async def parse_file(self, file: UploadFile) -> Tuple[pd.DataFrame, bytes, str]:
        content: bytes = await file.read()
        ext = os.path.splitext(file.filename or "")[1].lower()
        content_type = file.content_type or "application/octet-stream"

        if ext in [".xlsx", ".xls"]:
            # Excel
            df = pd.read_excel(io.BytesIO(content))
        else:
            # Default to CSV
            try:
                df = pd.read_csv(io.BytesIO(content))
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(content), encoding="latin-1")

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Parsed file is not a valid DataFrame")

        return df, content, content_type

    def create_documents(
        self, df: pd.DataFrame, filename: Optional[str] = None
    ) -> Tuple[List[Document], List[str], List[Dict[str, Any]]]:
        safe_df = df.fillna("").astype(str)
        records: List[Dict[str, str]] = safe_df.to_dict(orient="records")

        documents: List[Document] = []
        texts: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for row_index, record in enumerate(records):
            text = " | ".join(f"{key}: {value}" for key, value in record.items())
            metadata: Dict[str, Any] = {
                "row_index": row_index,
                "filename": filename or "",
                "columns": list(safe_df.columns),
            }
            documents.append(Document(text=text, metadata=metadata))
            texts.append(text)
            metadatas.append(metadata)

        return documents, texts, metadatas

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        # Use local SQLite cache
        cache = EmbeddingCache()
        return embed_with_cache(
            texts,
            client=self.openai_client,
            model=self.embedding_model_name,
            batch_size=100,
            cache=cache,
        )

    def index_into_pgvector(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        if not texts:
            return
        docs = [Document(text=t, metadata=m) for t, m in zip(texts, metadatas)]
        _ = build_or_update_vector_index(docs)

    def store_in_supabase(
        self,
        user_id: str,
        filename: str,
        file_size: int,
        df: pd.DataFrame,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> str:
        supabase = get_supabase_service_client()

        # Insert original_data row
        original_insert = supabase.table("original_data").insert(
            {
                "filename": filename,
                "file_size": file_size,
                "user_id": user_id,
                "metadata": {"columns": list(df.columns), "row_count": len(df)},
            }
        ).execute()

        if not getattr(original_insert, "data", None):
            raise RuntimeError("Failed to insert original_data row")
        original_data_id: str = original_insert.data[0]["id"]

        # Prepare chunk rows for data_chunks
        rows: List[Dict[str, Any]] = []
        for idx, (text, meta, emb) in enumerate(zip(texts, metadatas, embeddings)):
            rows.append(
                {
                    "original_data_id": original_data_id,
                    "chunk_index": idx,
                    "content": text,
                    "metadata": meta,
                    "embedding": emb,
                }
            )

        # Insert in batches to avoid payload limits
        batch_size = 500
        for start in range(0, len(rows), batch_size):
            batch = rows[start : start + batch_size]
            resp = supabase.table("data_chunks").insert(batch).execute()
            if getattr(resp, "error", None):
                raise RuntimeError(f"Failed to insert data_chunks batch: {resp.error}")

        return original_data_id

    def upsert_into_chroma(
        self,
        user_id: str,
        dataset_id: Optional[str],
        original_data_id: str,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> str:
        collection = get_or_create_collection_for(
            user_id=user_id,
            dataset_id=dataset_id,
            metadata={"user_id": user_id, "dataset_id": dataset_id},
            autoload=True,
        )

        ids = [f"{original_data_id}:{i}" for i in range(len(texts))]
        add_or_update_documents(
            collection=collection,
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        # Autosave to Supabase Storage if enabled
        try:
            autosave_collection_to_supabase(collection_name=collection.name)
        except Exception:
            # Non-fatal
            pass

        return collection.name
