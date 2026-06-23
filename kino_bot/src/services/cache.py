"""
Redis cache service — search, movie, stats, top-movies caching.
Task #19.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

import redis.asyncio as aioredis

from src.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.redis_url,
            password=settings.redis_password,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


class CacheService:
    """Typed cache wrappers with per-domain TTLs."""

    # ── Generic ───────────────────────────────────────────────────────────

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        try:
            r = await get_redis()
            raw = await r.get(key)
            return json.loads(raw) if raw else None
        except Exception as exc:
            logger.warning("Cache GET error for key=%s: %s", key, exc)
            return None

    @staticmethod
    async def set(key: str, value: Any, ttl: int = 300) -> None:
        try:
            r = await get_redis()
            await r.set(key, json.dumps(value, default=str), ex=ttl)
        except Exception as exc:
            logger.warning("Cache SET error for key=%s: %s", key, exc)

    @staticmethod
    async def delete(key: str) -> None:
        try:
            r = await get_redis()
            await r.delete(key)
        except Exception as exc:
            logger.warning("Cache DELETE error for key=%s: %s", key, exc)

    @staticmethod
    async def delete_pattern(pattern: str) -> int:
        try:
            r = await get_redis()
            keys = await r.keys(pattern)
            if keys:
                return await r.delete(*keys)
            return 0
        except Exception as exc:
            logger.warning("Cache DELETE_PATTERN error %s: %s", pattern, exc)
            return 0

    # ── Search cache ──────────────────────────────────────────────────────

    @staticmethod
    def _search_key(query: str, page: int) -> str:
        return f"search:{query.lower().strip()}:{page}"

    @classmethod
    async def get_search(cls, query: str, page: int) -> Optional[Any]:
        return await cls.get(cls._search_key(query, page))

    @classmethod
    async def set_search(cls, query: str, page: int, data: Any) -> None:
        await cls.set(cls._search_key(query, page), data, settings.cache_ttl_search)

    # ── Movie cache ───────────────────────────────────────────────────────

    @staticmethod
    def _movie_key(movie_id: int) -> str:
        return f"movie:{movie_id}"

    @classmethod
    async def get_movie(cls, movie_id: int) -> Optional[Any]:
        return await cls.get(cls._movie_key(movie_id))

    @classmethod
    async def set_movie(cls, movie_id: int, data: Any) -> None:
        await cls.set(cls._movie_key(movie_id), data, settings.cache_ttl_movie)

    @classmethod
    async def invalidate_movie(cls, movie_id: int) -> None:
        await cls.delete(cls._movie_key(movie_id))

    # ── Top movies cache ──────────────────────────────────────────────────

    @staticmethod
    def _top_key(period: str, limit: int) -> str:
        return f"top:{period}:{limit}"

    @classmethod
    async def get_top(cls, period: str, limit: int) -> Optional[Any]:
        return await cls.get(cls._top_key(period, limit))

    @classmethod
    async def set_top(cls, period: str, limit: int, data: Any) -> None:
        await cls.set(cls._top_key(period, limit), data, settings.cache_ttl_top)

    @classmethod
    async def invalidate_top(cls) -> None:
        await cls.delete_pattern("top:*")

    # ── Stats cache ───────────────────────────────────────────────────────

    @staticmethod
    def _stats_key(scope: str) -> str:
        return f"stats:{scope}"

    @classmethod
    async def get_stats(cls, scope: str) -> Optional[Any]:
        return await cls.get(cls._stats_key(scope))

    @classmethod
    async def set_stats(cls, scope: str, data: Any) -> None:
        await cls.set(cls._stats_key(scope), data, settings.cache_ttl_stats)

    @classmethod
    async def invalidate_stats(cls) -> None:
        await cls.delete_pattern("stats:*")

    # ── Rate limiting ──────────────────────────────────────────────────────

    @staticmethod
    async def check_rate_limit(key: str, limit: int, window: int = 60) -> bool:
        """Returns True if under limit, False if limit exceeded."""
        try:
            r = await get_redis()
            pipe = r.pipeline()
            await pipe.incr(key)
            await pipe.expire(key, window)
            results = await pipe.execute()
            current = results[0]
            return current <= limit
        except Exception as exc:
            logger.warning("Rate limit check error: %s", exc)
            return True  # Fail open

    # ── Session state ─────────────────────────────────────────────────────

    @staticmethod
    async def set_session(user_id: int, key: str, value: Any, ttl: int = 3600) -> None:
        r = await get_redis()
        await r.set(f"session:{user_id}:{key}", json.dumps(value, default=str), ex=ttl)

    @staticmethod
    async def get_session(user_id: int, key: str) -> Optional[Any]:
        r = await get_redis()
        raw = await r.get(f"session:{user_id}:{key}")
        return json.loads(raw) if raw else None

    @staticmethod
    async def delete_session(user_id: int, key: str) -> None:
        r = await get_redis()
        await r.delete(f"session:{user_id}:{key}")

    @staticmethod
    async def clear_user_session(user_id: int) -> None:
        r = await get_redis()
        keys = await r.keys(f"session:{user_id}:*")
        if keys:
            await r.delete(*keys)

    # ── Health check ──────────────────────────────────────────────────────

    @staticmethod
    async def ping() -> bool:
        try:
            r = await get_redis()
            return await r.ping()
        except Exception:
            return False
