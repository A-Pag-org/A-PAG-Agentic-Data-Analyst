from __future__ import annotations

from typing import List, Optional
import json
import re

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from ...core.config import settings


class DecompositionAgent:
    def __init__(self, *, llm: Optional[ChatOpenAI] = None, max_subqueries: Optional[int] = None):
        self.llm = llm or ChatOpenAI(
            api_key=settings.openai_api_key,
            model="gpt-4o-mini",
            temperature=0.1,
        )
        # Use config if present, else fallback
        self.max_subqueries = (
            max_subqueries
            if max_subqueries is not None
            else int(getattr(settings, "query_decomposition_max_sub_queries", 4))
        )

    async def decompose(self, *, question: str) -> List[str]:
        should_decompose: bool = bool(getattr(settings, "query_decomposition_enabled", True))
        if not should_decompose:
            return [question]

        if not settings.openai_api_key:
            return self._fallback_split(question)

        guidance = (
            "Break the user question into at most N short, non-overlapping sub-questions that "
            "together answer the original. Ensure each sub-question is self-contained. "
            "Use the same language as the question. Output ONLY valid JSON as: {\"sub_queries\":[...]}"
        )
        n = max(1, min(8, self.max_subqueries))
        messages = [
            SystemMessage(content="You are a precise query planner."),
            HumanMessage(content=f"N={n}\nQuestion: {question}\n\n{guidance}"),
        ]
        try:
            resp = await self.llm.ainvoke(messages)
            raw: str = (getattr(resp, "content", str(resp)) or "").strip()
            cleaned = self._strip_fences(raw)
            data = json.loads(cleaned)
            subqs = data.get("sub_queries") if isinstance(data, dict) else None
            if isinstance(subqs, list):
                subqs = [s.strip() for s in subqs if isinstance(s, str) and s.strip()]
                if subqs:
                    return subqs[: n]
        except Exception:
            pass
        return self._fallback_split(question)

    def _fallback_split(self, question: str) -> List[str]:
        text = (question or "").strip()
        if not text:
            return []
        # Heuristic splits; keep concise and self-contained
        candidates: List[str] = []
        # Split by question marks
        parts = [p.strip() for p in re.split(r"\?+\s*", text) if p.strip()]
        if len(parts) > 1:
            candidates.extend(parts)
        else:
            # Split on conjunctions/sequencers
            tmp = re.split(r"\b(?:and then|then|after that|followed by|and)\b", text, flags=re.IGNORECASE)
            tmp = [t.strip(", .;") for t in tmp if t and t.strip(", .;")]
            candidates.extend(tmp or [text])
        # Ensure max length and uniqueness
        seen = set()
        unique: List[str] = []
        for c in candidates:
            if c.lower() in seen:
                continue
            seen.add(c.lower())
            unique.append(c if c.endswith('?') else c + '?')
        return unique[: self.max_subqueries]

    def _strip_fences(self, s: str) -> str:
        s = s.strip()
        if s.startswith("```") and s.endswith("```"):
            s = s.strip("`")
            # Remove optional language hint lines
            lines = [ln for ln in s.splitlines() if ln.strip()]
            if lines and not lines[0].startswith("{"):
                lines = lines[1:]
            return "\n".join(lines).strip()
        return s
