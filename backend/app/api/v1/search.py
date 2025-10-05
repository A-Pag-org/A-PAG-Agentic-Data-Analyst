from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional

from ...services.query_engine import build_hybrid_query_engine
from ...services.chromadb_client import query_collection


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/query")
async def query(user_id: str = Query(...), q: str = Query(...)):
    try:
        engine = build_hybrid_query_engine(user_id=user_id)
        response = engine.query(q)
        return {
            "answer": str(response),
            "source_nodes": [
                {
                    "score": getattr(node, "score", None),
                    "text": node.get_content() if hasattr(node, "get_content") else getattr(node, "text", None),
                    "metadata": getattr(node, "metadata", {}),
                }
                for node in getattr(response, "source_nodes", []) or []
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/query_chroma")
async def query_chroma(
    user_id: str = Query(...),
    q: Optional[str] = Query(None),
    n_results: int = Query(8, ge=1, le=100),
    dataset_id: Optional[str] = Query(None),
    where: Optional[str] = Query(None, description="JSON for metadata filters"),
):
    try:
        where_dict: Optional[Dict[str, Any]] = None
        if where:
            import json as _json

            where_dict = _json.loads(where)

        result = query_collection(
            user_id=user_id,
            dataset_id=dataset_id,
            query_texts=[q] if q else None,
            n_results=n_results,
            where=where_dict,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
