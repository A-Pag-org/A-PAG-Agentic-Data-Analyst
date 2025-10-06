from __future__ import annotations

import json
from typing import Any, Optional

import redis

from ..core.config import settings

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    if not settings.redis_url:
        return None
    # Decode responses as str to simplify json handling
    _redis_client = redis.from_url(settings.redis_url, decode_responses=True)  # type: ignore[arg-type]
    return _redis_client


def cache_get(key: str) -> Any | None:
    client = get_redis_client()
    if client is None:
        return None
    raw = client.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
    client = get_redis_client()
    if client is None:
        return
    try:
        payload = json.dumps(value, separators=(",", ":"))
        ttl = ttl_seconds if ttl_seconds is not None else int(getattr(settings, "cache_ttl_seconds", 300))
        client.setex(key, ttl, payload)
    except Exception:
        # Best-effort caching should never break requests
        pass
