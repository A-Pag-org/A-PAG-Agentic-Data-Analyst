from fastapi import HTTPException, Request, status
from ..core.config import settings

async def verify_request_authentication(request: Request) -> None:
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
