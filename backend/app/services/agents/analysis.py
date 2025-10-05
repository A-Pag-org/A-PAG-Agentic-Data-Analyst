from __future__ import annotations

from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from ...core.config import settings


class AnalysisAgent:
    def __init__(self, *, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4o-mini", temperature=0.2)

    async def analyze(self, *, question: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        context_str = "\n\n".join(f"[{i+1}] {c.get('text','')}" for i, c in enumerate(contexts))
        messages = [
            SystemMessage(content=(
                "You are a senior data analyst. Answer precisely using the provided context. "
                "Cite source indices like [1], [2] when justifying. If uncertain, say so."
            )),
            HumanMessage(content=(
                f"Question: {question}\n\nContext:\n{context_str}\n\n"
                "Instructions: Provide a one-sentence direct answer first. "
                "Then list 2-4 concise bullet justifications with citations."
            )),
        ]
        resp = await self.llm.ainvoke(messages)
        content: str = getattr(resp, "content", str(resp)) or ""
        lines = [ln for ln in content.splitlines() if ln.strip()]
        answer = lines[0].strip() if lines else ""
        explanation = "\n".join(lines[1:]).strip() if len(lines) > 1 else None
        return {"answer": answer, "explanation": explanation}
