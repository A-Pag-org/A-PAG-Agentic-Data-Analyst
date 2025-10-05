from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .auth import verify_request_authentication

# Simple function-based middleware callable used with app.middleware('http')
async def auth_middleware(request: Request, call_next: Callable[[Request], Response]):
    await verify_request_authentication(request)
    response = await call_next(request)
    return response
