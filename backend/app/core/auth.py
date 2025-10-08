from fastapi import HTTPException, Request, status
from ..core.config import settings


def _is_public_request(request: Request) -> bool:
    """Return True if this request should bypass auth.

    We allow unauthenticated access to basic health and readiness endpoints,
    and we always permit OPTIONS requests to support CORS preflight.
    """
    # Always allow CORS preflight and HEAD
    method = (request.method or "").upper()
    if method in {"OPTIONS"}:
        return True

    # Normalize path and strip trailing slash
    path = (request.url.path or "").rstrip("/").lower()

    # Public endpoints that should be reachable without auth (production-safe)
    public_paths = {
        "/api/v1/health",
        "/api/v1/livez",
        "/api/v1/readyz",
        "/api/v1/metrics",  # Prometheus metrics (if enabled)
    }

    return method in {"GET", "HEAD"} and path in public_paths

async def verify_request_authentication(request: Request) -> None:
    # Allow-list public endpoints regardless of environment
    if _is_public_request(request):
        return

    # If unauthenticated access is explicitly allowed (same-origin, single-user)
    if settings.allow_unauthenticated:
        return

    expected_token = settings.auth_bearer_token
    if not expected_token:
        # If no token configured, permit all in development for convenience
        if settings.environment != "production":
            return
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth not configured")

    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    provided_token = auth_header.split(" ", 1)[1]
    if provided_token != expected_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
