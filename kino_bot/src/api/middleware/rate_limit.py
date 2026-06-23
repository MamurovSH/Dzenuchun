"""
Rate limiting middleware using Redis (#20).
"""
from __future__ import annotations

from fastapi import HTTPException, Request, status

from src.core.config import settings
from src.services.cache import CacheService


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    key = f"ratelimit:{client_ip}"
    allowed = await CacheService.check_rate_limit(
        key, settings.api_rate_limit_per_minute, window=60
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again in 60 seconds.",
        )
    return await call_next(request)
