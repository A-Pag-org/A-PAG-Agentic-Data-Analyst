from __future__ import annotations

from typing import List, Optional

from llama_index.core import Document, StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.postgres import PGVectorStore

from ..core.config import settings


def get_pgvector_store() -> PGVectorStore:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not set for PGVector store")
    store = PGVectorStore.from_params(
        database_url=settings.database_url,
        schema_name=settings.pgvector_schema,
        table_name=settings.pgvector_table,
        embed_dim=settings.embedding_dim,
    )
    return store


def build_or_update_vector_index(documents: List[Document]) -> VectorStoreIndex:
    # Ensure embed model is configured for consistent vectors
    Settings.embed_model = OpenAIEmbedding(model=settings.embedding_model, api_key=settings.openai_api_key)
    store = get_pgvector_store()
    storage_context = StorageContext.from_defaults(vector_store=store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    return index
