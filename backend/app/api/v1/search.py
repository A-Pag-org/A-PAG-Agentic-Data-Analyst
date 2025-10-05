from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ...services.query_engine import build_hybrid_query_engine


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
