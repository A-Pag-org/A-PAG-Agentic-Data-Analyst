from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
import time
from typing import Optional

try:
    from prometheus_client import Histogram, Counter  # type: ignore
except Exception:
    Histogram = None  # type: ignore
    Counter = None  # type: ignore
from pydantic import BaseModel

from ...services.agents import DataAnalysisAgent


router = APIRouter(prefix="/agents", tags=["agents"])

# Lazily define Prometheus metrics if library is present
_REQ_LATENCY: Optional[Histogram] = None
_REQ_COUNT: Optional[Counter] = None
if Histogram is not None and Counter is not None:
    try:
        _REQ_LATENCY = Histogram(
            "agents_analyze_latency_seconds",
            "Latency of /agents/analyze requests",
            buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        )
        _REQ_COUNT = Counter(
            "agents_analyze_total",
            "Total /agents/analyze calls",
            labelnames=("status",),
        )
    except Exception:
        _REQ_LATENCY = None
        _REQ_COUNT = None


class AnalyzeRequest(BaseModel):
    user_id: str
    query: str
    visualize: bool = False
    forecast: bool = False
    session_id: str | None = None


@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    start = time.perf_counter()
    status_label = "success"
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
        status_label = "error"
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        if _REQ_LATENCY is not None:
            try:
                _REQ_LATENCY.observe(time.perf_counter() - start)
            except Exception:
                pass
        if _REQ_COUNT is not None:
            try:
                _REQ_COUNT.labels(status=status_label).inc()
            except Exception:
                pass
