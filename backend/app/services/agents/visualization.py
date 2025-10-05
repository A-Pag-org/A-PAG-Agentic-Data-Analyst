from __future__ import annotations

from typing import Any, Dict, List, Optional
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from ...core.config import settings


class VisualizationAgent:
    def __init__(self, *, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4o-mini", temperature=0.2)

    async def maybe_visualize(self, *, question: str, contexts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        sample_context = "\n\n".join(c.get("text", "") for c in contexts[:5])
        guidance = (
            "If a simple chart would help answer the user's question, output ONLY a valid Vega-Lite v5 JSON spec. "
            "If not helpful, respond with the exact word: NONE."
        )
        messages = [
            SystemMessage(content="You design clear, minimalist Vega-Lite charts."),
            HumanMessage(content=f"{guidance}\n\nQuestion: {question}\n\nContext:\n{sample_context}"),
        ]
        resp = await self.llm.ainvoke(messages)
        raw = (getattr(resp, "content", str(resp)) or "").strip()
        if raw.upper() == "NONE":
            return None
        try:
            spec = json.loads(raw)
            if isinstance(spec, dict):
                return spec
        except Exception:
            return None
        return None
