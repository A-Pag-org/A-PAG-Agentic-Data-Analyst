from fastapi import APIRouter
from . import health
from . import ingest
from . import search
from . import agents
from . import export

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(ingest.router)
api_router.include_router(search.router)
api_router.include_router(agents.router)
api_router.include_router(export.router)
