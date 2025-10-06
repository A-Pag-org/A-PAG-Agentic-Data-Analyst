from __future__ import annotations

import io
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from ...services.supabase_client import get_supabase_service_client


router = APIRouter(prefix="/export", tags=["export"])


def _parse_row_text_to_dict(text: str) -> Dict[str, str]:
    """Parses a row string in the form "col1: val1 | col2: val2 | ..." into a dict.

    This parsing mirrors how rows were serialized in DataProcessor.create_documents.
    """
    if not text:
        return {}
    parts = [p.strip() for p in text.split("|")]
    result: Dict[str, str] = {}
    for part in parts:
        if not part:
            continue
        # split only on first ':' to preserve values containing ':'
        if ":" in part:
            key, value = part.split(":", 1)
            result[key.strip()] = value.strip()
        else:
            # if malformed, store as-is under an empty key suffix
            result[part] = ""
    return result


def _fetch_rows_from_supabase(original_data_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_service_client()
    # Fetch chunk contents in original order
    resp = (
        supabase
        .table("data_chunks")
        .select("content")
        .eq("original_data_id", original_data_id)
        .order("chunk_index", desc=False)
        .execute()
    )
    data = getattr(resp, "data", None) or []
    rows: List[Dict[str, Any]] = []
    for item in data:
        content: str = item.get("content", "")
        row_dict = _parse_row_text_to_dict(content)
        rows.append(row_dict)
    return rows


@router.get("/csv")
async def export_csv(
    original_data_id: str = Query(..., description="ID of the uploaded dataset to export"),
    filename: Optional[str] = Query(None, description="Optional download filename, defaults to export.csv"),
):
    rows = _fetch_rows_from_supabase(original_data_id)
    if not rows:
        raise HTTPException(status_code=404, detail="No data found for provided original_data_id")

    df = pd.DataFrame(rows)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")
    headers = {
        "Content-Disposition": f"attachment; filename=\"{filename or 'export.csv'}\"",
        "Cache-Control": "no-store",
    }
    return StreamingResponse(io.BytesIO(csv_bytes), media_type="text/csv", headers=headers)


@router.get("/excel")
async def export_excel(
    original_data_id: str = Query(..., description="ID of the uploaded dataset to export"),
    date_column: Optional[str] = Query(None, description="Name of date column to filter on"),
    start_date: Optional[str] = Query(None, description="Inclusive start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Inclusive end date (ISO format)"),
    filename: Optional[str] = Query(None, description="Optional download filename, defaults to export.xlsx"),
):
    rows = _fetch_rows_from_supabase(original_data_id)
    if not rows:
        raise HTTPException(status_code=404, detail="No data found for provided original_data_id")

    df = pd.DataFrame(rows)

    # Optional date filtering
    if date_column and (start_date or end_date):
        if date_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"date_column '{date_column}' not found in data")
        dates = pd.to_datetime(df[date_column], errors="coerce")
        mask = pd.Series([True] * len(df))
        if start_date:
            start_dt = pd.to_datetime(start_date, errors="coerce")
            if pd.isna(start_dt):
                raise HTTPException(status_code=400, detail="Invalid start_date format")
            mask &= dates >= start_dt
        if end_date:
            end_dt = pd.to_datetime(end_date, errors="coerce")
            if pd.isna(end_dt):
                raise HTTPException(status_code=400, detail="Invalid end_date format")
            mask &= dates <= end_dt
        df = df[mask]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Data", index=False)
    output.seek(0)

    headers = {
        "Content-Disposition": f"attachment; filename=\"{filename or 'export.xlsx'}\"",
        "Cache-Control": "no-store",
    }
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
