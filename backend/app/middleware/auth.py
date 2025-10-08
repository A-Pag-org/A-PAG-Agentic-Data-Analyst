from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from ..core.auth import verify_request_authentication

# Simple function-based middleware callable used with app.middleware('http')
async def auth_middleware(request: Request, call_next: Callable[[Request], Response]):
    try:
        await verify_request_authentication(request)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return await call_next(request)
