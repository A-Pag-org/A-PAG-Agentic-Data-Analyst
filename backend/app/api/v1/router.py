from fastapi import APIRouter

try:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest, REGISTRY  # type: ignore
except Exception:
    CONTENT_TYPE_LATEST = None  # type: ignore
    generate_latest = None  # type: ignore
    REGISTRY = None  # type: ignore
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

        # Expose Prometheus metrics if prometheus_client is available
        if generate_latest is not None and CONTENT_TYPE_LATEST is not None:
            @router.get("/metrics")
            async def metrics():  # type: ignore[no-redef]
                content = generate_latest(REGISTRY) if REGISTRY is not None else b""
                from fastapi.responses import Response
                return Response(content=content, media_type=CONTENT_TYPE_LATEST)

    return router
