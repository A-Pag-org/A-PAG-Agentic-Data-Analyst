from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field

from ...services.forecasting_service import ForecastingService
from ...services.data_loaders import uploadfile_to_dataframe

router = APIRouter(prefix="/forecast", tags=["forecast"])


class ForecastFromJsonRequest(BaseModel):
    data: list[dict[str, Any]] = Field(..., description="Tabular rows with at least date and target columns")
    target_column: str
    date_column: Optional[str] = None
    periods: int = 30
    freq: str = "D"


@router.post("/from-json")
async def forecast_from_json(req: ForecastFromJsonRequest):
    try:
        df = pd.DataFrame(req.data)
        service = ForecastingService()
        result = await service.generate_forecast(
            df,
            target_column=req.target_column,
            date_column=req.date_column,
            periods=int(req.periods),
            freq=req.freq,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/from-file")
async def forecast_from_file(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    date_column: Optional[str] = Form(None),
    periods: int = Form(30),
    freq: str = Form("D"),
):
    try:
        df = await uploadfile_to_dataframe(file)
        service = ForecastingService()
        result = await service.generate_forecast(
            df,
            target_column=target_column,
            date_column=date_column,
            periods=int(periods),
            freq=freq,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
