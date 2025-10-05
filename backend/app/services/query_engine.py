from __future__ import annotations

from typing import List

from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI

from ..core.config import settings
from .data_loaders import load_user_documents_from_supabase
from .vector_store_pg import get_pgvector_store


def build_hybrid_query_engine(user_id: str) -> RetrieverQueryEngine:
    # Configure LLM and embedding model for LlamaIndex
    if settings.openai_api_key:
        Settings.llm = LlamaOpenAI(api_key=settings.openai_api_key)
    Settings.embed_model = OpenAIEmbedding(model=settings.embedding_model, api_key=settings.openai_api_key)

    # Load documents for BM25
    documents: List[Document] = load_user_documents_from_supabase(user_id=user_id, limit=None)

    # BM25 retriever over all user docs
    bm25 = BM25Retriever.from_documents(documents, similarity_top_k=settings.retriever_top_k)

    # Vector retriever via PGVector store
    vector_store = get_pgvector_store()
    vector_index = VectorStoreIndex.from_vector_store(vector_store)
    vector_retriever = vector_index.as_retriever(similarity_top_k=settings.retriever_top_k)

    # Fusion retriever combines both
    fusion = QueryFusionRetriever(retrievers=[bm25, vector_retriever], num_queries=1)

    # Re-ranking with cross encoder
    reranker = SentenceTransformerRerank(
        model=settings.reranker_model,
        top_n=settings.reranker_top_n,
    )

    return RetrieverQueryEngine(retriever=fusion, node_postprocessors=[reranker])
