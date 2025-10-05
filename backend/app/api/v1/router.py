from fastapi import APIRouter
from . import health
from . import ingest

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(ingest.router)
