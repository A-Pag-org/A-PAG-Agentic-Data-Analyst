from fastapi import APIRouter
import time

try:
    import psutil  # type: ignore
except Exception:
    psutil = None  # type: ignore

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/livez")
async def liveness():
    # Simple fast response to indicate process is alive
    return {"status": "ok"}


@router.get("/readyz")
async def readiness():
    # Basic readiness checks; extend with DB/ping checks as needed
    checks = {"app_start_time": time.time()}
    if psutil:
        try:
            mem = psutil.virtual_memory()
            checks.update({
                "memory_available": mem.available,
                "memory_percent": mem.percent,
            })
        except Exception:
            pass
    return {"status": "ok", "checks": checks}
