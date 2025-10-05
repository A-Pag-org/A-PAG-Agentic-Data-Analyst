from fastapi import APIRouter
from app.api.v1.endpoints import chat, data, analysis, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])