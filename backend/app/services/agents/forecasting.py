from __future__ import annotations

from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from ...core.config import settings


class ForecastingAgent:
    def __init__(self, *, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4o-mini", temperature=0.2)

    async def maybe_forecast(self, *, question: str, contexts: List[Dict[str, Any]]) -> Optional[str]:
        messages = [
            SystemMessage(content=(
                "You provide cautious, assumptions-explicit short-term forecasts based on available context only. "
                "Avoid fabricating data. Include uncertainties."
            )),
            HumanMessage(content=(
                f"Question: {question}\n\nContext (snippets):\n" + "\n\n".join(c.get("text", "") for c in contexts[:6]) +
                "\n\nOutput: 3-5 bullet points forecasting implications relevant to the question."
            )),
        ]
        resp = await self.llm.ainvoke(messages)
        content = getattr(resp, "content", str(resp)) or ""
        text = content.strip()
        return text if text else None
