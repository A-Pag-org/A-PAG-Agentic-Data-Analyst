from __future__ import annotations

import gzip
import io
import json
from typing import Any, Dict, List, Optional, Tuple

import chromadb

from ..core.config import settings
from .supabase_client import get_supabase_service_client
from .embeddings_cache import embed_with_cache, EmbeddingCache
from openai import OpenAI

# Singleton clients to avoid re-initialization in serverless
_chroma_client: Optional[Any] = None
_openai_client: Optional[OpenAI] = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY must be set for Chroma queries that require embeddings.")
        _openai_client = OpenAI(api_key=settings.openai_api_key)
    return _openai_client


def get_chroma_client() -> Any:
    """Return a Chroma client based on configuration.

    - memory: in-memory ephemeral client (serverless-friendly)
    - persistent: on-disk persistent client (uses CHROMA_PERSIST_DIR)
    """
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client

    backend = (settings.chroma_backend or "memory").lower()
    if backend == "persistent":
        persist_dir = settings.chroma_persist_dir or "chroma_index"
        _chroma_client = chromadb.PersistentClient(path=persist_dir)
    else:
        # Default to ephemeral in-memory
        _chroma_client = chromadb.Client()
    return _chroma_client


def collection_name_for(user_id: str, dataset_id: Optional[str] = None) -> str:
    scope = (settings.chroma_dataset_scope or "per_user").lower()
    if scope == "per_dataset" and dataset_id:
        return f"user_{user_id}_dataset_{dataset_id}"
    return f"user_{user_id}"


def get_or_create_collection_for(
    *, user_id: str, dataset_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, autoload: bool = True
):
    client = get_chroma_client()
    name = collection_name_for(user_id=user_id, dataset_id=dataset_id)
    base_meta: Dict[str, Any] = {
        "user_id": user_id,
        "dataset_id": dataset_id,
        "scope": settings.chroma_dataset_scope,
        "backend": settings.chroma_backend,
    }
    if metadata:
        base_meta.update(metadata)

    coll = client.get_or_create_collection(name=name, metadata=base_meta)

    if autoload and settings.chroma_autosave:
        try:
            # Only attempt autoload if empty
            if coll.count() == 0:
                _try_autoload_collection_from_supabase(collection_name=name)
        except Exception:
            # Autoload best effort; do not hard fail
            pass

    return coll


def add_or_update_documents(
    *,
    collection,
    ids: List[str],
    documents: Optional[List[str]] = None,
    metadatas: Optional[List[Dict[str, Any]]] = None,
    embeddings: Optional[List[List[float]]] = None,
    batch_size: int = 500,
) -> None:
    """Upsert documents into a Chroma collection. If duplicates exist, delete then re-add.

    Processes in batches to avoid payload limits.
    """
    if not ids:
        return

    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        batch_ids = ids[start:end]
        batch_docs = documents[start:end] if documents else None
        batch_metas = metadatas[start:end] if metadatas else None
        batch_embs = embeddings[start:end] if embeddings else None
        try:
            collection.add(ids=batch_ids, documents=batch_docs, metadatas=batch_metas, embeddings=batch_embs)
        except Exception:
            # Overwrite strategy: delete then add
            try:
                collection.delete(ids=batch_ids)
            except Exception:
                # Ignore failures; we'll try to add anyway
                pass
            collection.add(ids=batch_ids, documents=batch_docs, metadatas=batch_metas, embeddings=batch_embs)


def _export_collection_payload(collection) -> Dict[str, Any]:
    total = collection.count()
    payload: Dict[str, Any] = {
        "name": collection.name,
        "metadata": getattr(collection, "metadata", None) or {},
        "items": {"ids": [], "documents": [], "metadatas": [], "embeddings": []},
    }
    if total == 0:
        return payload

    page_size = 1000
    fetched = 0
    while fetched < total:
        chunk = collection.get(
            limit=page_size,
            offset=fetched,
            include=["documents", "metadatas", "embeddings"],
        )
        payload["items"]["ids"].extend(chunk.get("ids", []))
        payload["items"]["documents"].extend(chunk.get("documents", []))
        payload["items"]["metadatas"].extend(chunk.get("metadatas", []))
        payload["items"]["embeddings"].extend(chunk.get("embeddings", []))
        fetched += len(chunk.get("ids", []))
        if len(chunk.get("ids", [])) == 0:
            break

    return payload


def autosave_collection_to_supabase(*, collection_name: str) -> None:
    if not settings.chroma_autosave:
        return
    client = get_chroma_client()
    # Resolve collection object
    coll = client.get_collection(name=collection_name)
    payload = _export_collection_payload(coll)
    raw = json.dumps(payload).encode("utf-8")
    gz = gzip.compress(raw)

    supabase = get_supabase_service_client()
    bucket = settings.chroma_supabase_bucket
    storage = supabase.storage.from_(bucket)
    path = f"{collection_name}.json.gz"
    storage.upload(path=path, file=io.BytesIO(gz), file_options={"contentType": "application/json+gzip", "upsert": True})


def _try_autoload_collection_from_supabase(*, collection_name: str) -> bool:
    supabase = get_supabase_service_client()
    bucket = settings.chroma_supabase_bucket
    storage = supabase.storage.from_(bucket)
    path = f"{collection_name}.json.gz"
    try:
        data: bytes = storage.download(path)  # type: ignore[assignment]
    except Exception:
        return False

    try:
        raw = gzip.decompress(data)
        payload = json.loads(raw.decode("utf-8"))
    except Exception:
        return False

    items = payload.get("items") or {}
    ids: List[str] = items.get("ids") or []
    if not ids:
        return False

    documents: List[str] = items.get("documents") or []
    metadatas: List[Dict[str, Any]] = items.get("metadatas") or []
    embeddings: List[List[float]] = items.get("embeddings") or []

    client = get_chroma_client()
    coll = client.get_or_create_collection(name=collection_name)
    add_or_update_documents(
        collection=coll,
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return True


def load_collection_from_supabase(*, collection_name: str) -> bool:
    """Public wrapper to load a collection snapshot from Supabase Storage.

    Returns True if any items were loaded.
    """
    return _try_autoload_collection_from_supabase(collection_name=collection_name)


def list_user_collections(user_id: str) -> List[Dict[str, Any]]:
    client = get_chroma_client()
    out: List[Dict[str, Any]] = []
    for c in client.list_collections():
        meta = getattr(c, "metadata", None) or {}
        if meta.get("user_id") == user_id or c.name.startswith(f"user_{user_id}"):
            out.append({"name": c.name, "metadata": meta})
    return out


def delete_collection(*, user_id: str, dataset_id: Optional[str] = None) -> None:
    client = get_chroma_client()
    name = collection_name_for(user_id=user_id, dataset_id=dataset_id)
    try:
        client.delete_collection(name=name)
    except Exception:
        # Best effort
        pass


def query_collection(
    *,
    user_id: str,
    dataset_id: Optional[str] = None,
    query_texts: Optional[List[str]] = None,
    query_embeddings: Optional[List[List[float]]] = None,
    n_results: int = 8,
    where: Optional[Dict[str, Any]] = None,
    where_document: Optional[Dict[str, Any]] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    include = include or ["documents", "metadatas", "distances"]
    coll = get_or_create_collection_for(user_id=user_id, dataset_id=dataset_id)

    if query_embeddings is None:
        if not query_texts:
            raise ValueError("Either query_texts or query_embeddings must be provided")
        # Embed with local cache
        client = _get_openai_client()
        vectors = embed_with_cache(
            query_texts,
            client=client,
            model=settings.embedding_model,
            batch_size=50,
            cache=EmbeddingCache(),
        )
        query_embeddings = vectors

    return coll.query(
        query_texts=query_texts,
        query_embeddings=query_embeddings,
        n_results=n_results,
        where=where,
        where_document=where_document,
        include=include,
    )
