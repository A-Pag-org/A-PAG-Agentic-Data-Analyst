from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...services.agents import DataAnalysisAgent


router = APIRouter(prefix="/agents", tags=["agents"])


class AnalyzeRequest(BaseModel):
    user_id: str
    query: str
    visualize: bool = False
    forecast: bool = False
    session_id: str | None = None


@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        agent = DataAnalysisAgent()
        result = await agent.process_query(
            req.query,
            {
                "user_id": req.user_id,
                "visualize": req.visualize,
                "forecast": req.forecast,
                "session_id": req.session_id,
            },
        )
        return asdict(result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
