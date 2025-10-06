from __future__ import annotations

import os

from fastapi import FastAPI
import os

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration
except Exception:
    sentry_sdk = None  # type: ignore
    FastApiIntegration = None  # type: ignore
    StarletteIntegration = None  # type: ignore
from .api.v1.router import get_api_router
from .middleware.auth import auth_middleware

def create_app(*, minimal: bool | None = None) -> FastAPI:
    """Create the FastAPI application.

    If minimal is None, it is inferred from env var APP_MINIMAL (truthy/falsey).
    When minimal is True, only lightweight routes are mounted to speed up tests.
    """
    if minimal is None:
        minimal = os.getenv("APP_MINIMAL", "").lower() in {"1", "true", "yes", "on"}

    # Initialize Sentry once per process if configured
    if sentry_sdk is not None and (os.getenv("SENTRY_DSN") or os.getenv("BACKEND_SENTRY_DSN")):
        try:
            sentry_sdk.init(
                dsn=os.getenv("SENTRY_DSN") or os.getenv("BACKEND_SENTRY_DSN"),
                enable_tracing=True,
                traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
                profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.0")),
                environment=os.getenv("SENTRY_ENVIRONMENT") or os.getenv("ENVIRONMENT") or "development",
                integrations=[
                    *( [FastApiIntegration()] if FastApiIntegration else [] ),
                    *( [StarletteIntegration()] if StarletteIntegration else [] ),
                ],
            )
        except Exception:
            # Proceed without Sentry if initialization fails
            pass

    app = FastAPI(title="Backend API", version="0.1.0")

    # Middleware
    app.middleware('http')(auth_middleware)

    # Routers
    app.include_router(get_api_router(minimal=minimal), prefix="/api/v1")

    return app

# Expose a module-level app for ASGI servers that don't use factory mode.
# To avoid import-time side effects in tests, this can be disabled by setting
# APP_AUTOINIT=0 in the environment before importing this module.
if os.getenv("APP_AUTOINIT", "1") not in {"0", "false", "no", "off"}:
    app = create_app()
