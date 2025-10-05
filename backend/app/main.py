from fastapi import FastAPI
from .api.v1.router import api_router
from .middleware.auth import auth_middleware

def create_app() -> FastAPI:
    app = FastAPI(title="Backend API", version="0.1.0")

    # Middleware
    app.middleware('http')(auth_middleware)

    # Routers
    app.include_router(api_router, prefix="/api/v1")

    return app
