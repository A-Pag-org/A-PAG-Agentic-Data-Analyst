from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .retrieval import RetrievalAgent
from .analysis import AnalysisAgent
from .visualization import VisualizationAgent
from .forecasting import ForecastingAgent


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

    async def process_query(self, query: str, context: Dict[str, Any]):
        user_id: Optional[str] = (context or {}).get("user_id")
        if not user_id:
            raise ValueError("user_id is required in context")

        do_visualize: bool = bool((context or {}).get("visualize", False))
        do_forecast: bool = bool((context or {}).get("forecast", False))

        # 1) Retrieve relevant context
        sources = await self.retrieval_agent.retrieve(user_id=user_id, query=query)

        # 2) Analyze and answer
        analysis = await self.analysis_agent.analyze(question=query, contexts=sources)

        # 3) Optional visualization
        vis_spec: Optional[Dict[str, Any]] = None
        if do_visualize:
            vis_spec = await self.visualization_agent.maybe_visualize(question=query, contexts=sources)

        # 4) Optional forecasting
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
