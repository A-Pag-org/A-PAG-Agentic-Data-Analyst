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
from ..session_service import SessionService


@dataclass
class AgentResponse:
    answer: str
    sources: List[Dict[str, Any]]
    explanation: Optional[str] = None
    visualization_spec: Optional[Dict[str, Any]] = None
    forecast: Optional[str] = None
    session_id: Optional[str] = None


class DataAnalysisAgent:
    def __init__(self):
        # Share a single LLM across sub-agents when possible
        self.retrieval_agent = RetrievalAgent()
        self.analysis_agent = AnalysisAgent()
        self.visualization_agent = VisualizationAgent()
        self.forecasting_agent = ForecastingAgent()
        self.decomposition_agent = DecompositionAgent()

    async def decompose_query(self, query: str, *, history: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        return await self.decomposition_agent.decompose(question=query, history=history or [])

    async def process_query(self, query: str, context: Dict[str, Any]):
        user_id: Optional[str] = (context or {}).get("user_id")
        if not user_id:
            raise ValueError("user_id is required in context")

        do_visualize: bool = bool((context or {}).get("visualize", False))
        do_forecast: bool = bool((context or {}).get("forecast", False))
        session_id: Optional[str] = (context or {}).get("session_id")

        # Load limited conversation history for continuity
        history: List[Dict[str, Any]] = SessionService.load_history(session_id=session_id)

        # 1) Query decomposition (optional)
        sub_queries: List[str]
        if bool(getattr(settings, "query_decomposition_enabled", True)):
            sub_queries = await self.decompose_query(query, history=history)
            if not sub_queries:
                sub_queries = [query]
        else:
            sub_queries = [query]

        # 2) Retrieve relevant context (delegate multi-query to RetrievalAgent)
        sources = await self.retrieval_agent.retrieve(
            user_id=user_id,
            query=sub_queries if len(sub_queries) > 1 else sub_queries[0],
        )

        # 3) Analysis phase
        analysis = await self.analysis_agent.analyze(sources, query, history=history)
        # Make insights payload for downstream steps
        insights: Dict[str, Any] = {
            "question": query,
            **({k: v for k, v in analysis.items()} if isinstance(analysis, dict) else {"answer": str(analysis)}),
            "sources": sources,
        }

        # 4) Visualization planning
        viz_configs: List[Dict[str, Any]] = []
        if do_visualize:
            # Prefer explicit planning based on insights; fallback to context-based suggestion
            planned = await self.visualization_agent.plan_visualizations(insights)
            if planned:
                viz_configs = planned
            else:
                maybe = await self.visualization_agent.maybe_visualize(question=query, contexts=sources)
                if isinstance(maybe, dict):
                    viz_configs = [maybe]

        # 5) Forecasting (if applicable)
        forecast_text: Optional[str] = None
        if do_forecast:
            forecast_text = await self.forecasting_agent.forecast(insights)

        # 6) Persist/update conversation session
        user_turn = {"role": "user", "content": query}
        assistant_turn = {"role": "assistant", "answer": analysis.get("answer", ""), "explanation": analysis.get("explanation")}
        if session_id:
            SessionService.append_turn(session_id=session_id, user_turn=user_turn, assistant_turn=assistant_turn, sources=sources)
        else:
            session_id = SessionService.create_session(user_id=user_id, user_turn=user_turn, assistant_turn=assistant_turn, sources=sources)

        # Maintain backwards-compatible response while returning richer structure to API
        return AgentResponse(
            answer=analysis.get("answer", ""),
            explanation=analysis.get("explanation"),
            sources=sources,
            visualization_spec=(viz_configs[0] if viz_configs else None),
            forecast=forecast_text,
            session_id=session_id,
        )
