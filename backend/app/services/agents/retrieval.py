from __future__ import annotations

from typing import Any, Dict, List
import asyncio

from ..query_engine import build_hybrid_query_engine


class RetrievalAgent:
    def __init__(self, *, top_k: int | None = None):
        self.top_k = top_k

    async def retrieve(self, *, user_id: str, query: str) -> List[Dict[str, Any]]:
        engine = build_hybrid_query_engine(user_id=user_id)
        # LlamaIndex query is synchronous; run it in a thread to avoid blocking
        response = await asyncio.to_thread(engine.query, query)
        items: List[Dict[str, Any]] = []
        for node in getattr(response, "source_nodes", []) or []:
            text = node.get_content() if hasattr(node, "get_content") else getattr(node, "text", None)
            metadata = getattr(node, "metadata", {})
            score = getattr(node, "score", None)
            items.append({"text": text, "metadata": metadata, "score": score})
        return items
