from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from ...services.data_processor import DataProcessor

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    dataset_id: Optional[str] = Form(None),
):
    try:
        processor = DataProcessor()
        result = await processor.process_upload(file=file, user_id=user_id, dataset_id=dataset_id)
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
