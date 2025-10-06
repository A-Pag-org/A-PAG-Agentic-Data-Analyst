from fastapi import APIRouter
from . import health


def get_api_router(minimal: bool = False) -> APIRouter:
    """Build the API router.

    When minimal=True, only include lightweight routes that have no heavy
    third-party dependencies. This is useful for fast unit/integration tests
    that do not require the full RAG stack to be importable.
    """
    router = APIRouter()
    router.include_router(health.router, tags=["health"])

    if not minimal:
        # Import heavy routes lazily to avoid importing large dependencies
        # in test/minimal environments.
        from . import ingest, search, agents, export, evaluation  # noqa: WPS433

        router.include_router(ingest.router)
        router.include_router(search.router)
        router.include_router(agents.router)
        router.include_router(export.router)
        router.include_router(evaluation.router)

    return router
