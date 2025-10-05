from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import asyncio

from .retrieval import RetrievalAgent
from .analysis import AnalysisAgent
from .visualization import VisualizationAgent
from .forecasting import ForecastingAgent
from .decomposition import DecompositionAgent
from ...core.config import settings


@dataclass
class AgentResponse:
    answer: str
    sources: List[Dict[str, Any]]
    explanation: Optional[str] = None
    visualization_spec: Optional[Dict[str, Any]] = None
    forecast: Optional[str] = None


class DataAnalysisAgent:
    def __init__(self):
        # Share a single LLM across sub-agents when possible
        self.retrieval_agent = RetrievalAgent()
        self.analysis_agent = AnalysisAgent()
        self.visualization_agent = VisualizationAgent()
        self.forecasting_agent = ForecastingAgent()
        self.decomposition_agent = DecompositionAgent()

    async def decompose_query(self, query: str) -> List[str]:
        return await self.decomposition_agent.decompose(question=query)

    async def process_query(self, query: str, context: Dict[str, Any]):
        user_id: Optional[str] = (context or {}).get("user_id")
        if not user_id:
            raise ValueError("user_id is required in context")

        do_visualize: bool = bool((context or {}).get("visualize", False))
        do_forecast: bool = bool((context or {}).get("forecast", False))

        # 1) Query decomposition (optional)
        sub_queries: List[str]
        if bool(getattr(settings, "query_decomposition_enabled", True)):
            sub_queries = await self.decompose_query(query)
            if not sub_queries:
                sub_queries = [query]
        else:
            sub_queries = [query]

        # 2) Retrieve relevant context (delegate multi-query to RetrievalAgent)
        sources = await self.retrieval_agent.retrieve(
            user_id=user_id,
            query=sub_queries if len(sub_queries) > 1 else sub_queries[0],
        )

        # 3) Analyze and answer
        analysis = await self.analysis_agent.analyze(question=query, contexts=sources)

        # 4) Optional visualization
        vis_spec: Optional[Dict[str, Any]] = None
        if do_visualize:
            vis_spec = await self.visualization_agent.maybe_visualize(question=query, contexts=sources)

        # 5) Optional forecasting
        forecast_text: Optional[str] = None
        if do_forecast:
            forecast_text = await self.forecasting_agent.maybe_forecast(question=query, contexts=sources)

        return AgentResponse(
            answer=analysis.get("answer", ""),
            explanation=analysis.get("explanation"),
            sources=sources,
            visualization_spec=vis_spec,
            forecast=forecast_text,
        )
