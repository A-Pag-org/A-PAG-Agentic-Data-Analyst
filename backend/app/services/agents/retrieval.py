from __future__ import annotations

from typing import Any, Dict, List, Union, Optional
import asyncio

from ..query_engine import build_hybrid_query_engine
from ...core.config import settings


class RetrievalAgent:
    def __init__(self, *, top_k: int | None = None):
        self.top_k = top_k

    async def retrieve(self, *, user_id: str, query: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """Retrieve context items for one or many queries.

        When given a list of queries, executes in parallel and returns a
        deduplicated, score-sorted list capped by a configurable limit.
        """
        engine = build_hybrid_query_engine(user_id=user_id)

        async def query_once(single_query: str) -> List[Dict[str, Any]]:
            # LlamaIndex query is synchronous; run it in a thread to avoid blocking
            response = await asyncio.to_thread(engine.query, single_query)
            items: List[Dict[str, Any]] = []
            for node in getattr(response, "source_nodes", []) or []:
                text = node.get_content() if hasattr(node, "get_content") else getattr(node, "text", None)
                metadata = getattr(node, "metadata", {})
                score = getattr(node, "score", None)
                items.append({"text": text, "metadata": metadata, "score": score})
            # Optional Cohere rerank
            provider = (settings.reranker_provider or "local").lower()
            if provider == "cohere" and settings.cohere_api_key and items:
                try:
                    import cohere  # type: ignore

                    client = cohere.Client(api_key=settings.cohere_api_key)
                    docs = [it.get("text") or "" for it in items]
                    top_n = int(getattr(settings, "reranker_top_n", 5))
                    rr = client.rerank(
                        model=getattr(settings, "cohere_reranker_model", "rerank-3.5"),
                        query=single_query,
                        documents=docs,
                        top_n=min(top_n, len(docs)),
                    )
                    # rr.results may include entries with index and relevance_score
                    scores_by_index: Dict[int, float] = {}
                    results = getattr(rr, "results", []) or getattr(rr, "reranked_documents", []) or []
                    for res in results:
                        # Cohere SDK structures may vary; try both
                        idx = getattr(res, "index", None)
                        if idx is None and isinstance(res, dict):
                            idx = res.get("index")
                        score = getattr(res, "relevance_score", None)
                        if score is None and isinstance(res, dict):
                            score = res.get("relevance_score")
                        if isinstance(idx, int) and isinstance(score, (int, float)):
                            scores_by_index[idx] = float(score)
                    # Update items with scores and reorder
                    for i, it in enumerate(items):
                        if i in scores_by_index:
                            it["score"] = scores_by_index[i]
                    items.sort(key=lambda x: (x.get("score") if x.get("score") is not None else float("-inf")), reverse=True)
                    # Cap to top_n after rerank
                    items = items[:top_n]
                except Exception:
                    # If Cohere rerank fails, fall back to original order
                    pass
            return items

        if isinstance(query, str):
            return await query_once(query)

        # Multiple sub-queries: fan-out, flatten, deduplicate, sort, cap
        tasks = [query_once(q) for q in query if isinstance(q, str) and q.strip()]
        if not tasks:
            return []
        batches = await asyncio.gather(*tasks)
        flat: List[Dict[str, Any]] = [item for batch in batches for item in batch]

        # Deduplicate by text; keep higher score when duplicates collide
        best_by_text: Dict[str, Dict[str, Any]] = {}
        for item in flat:
            text_key = (item.get("text") or "").strip()
            if not text_key:
                continue
            prev = best_by_text.get(text_key)
            if prev is None or (item.get("score") or float("-inf")) > (prev.get("score") or float("-inf")):
                best_by_text[text_key] = item
        deduped = list(best_by_text.values())

        # Sort by score desc; None scored items last
        deduped.sort(key=lambda x: (x.get("score") if x.get("score") is not None else float("-inf")), reverse=True)

        limit = int(getattr(settings, "query_decomposition_context_limit", 12))
        return deduped[:limit]
