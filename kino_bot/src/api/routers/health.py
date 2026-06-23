"""
Health Check endpoint (#17) — CPU, RAM, Disk, DB, Redis, Telegram.
"""
from __future__ import annotations

import time
from datetime import datetime

import psutil
from fastapi import APIRouter
from sqlalchemy import text

from src.db.base import AsyncSessionFactory
from src.services.cache import CacheService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    start = time.monotonic()

    # DB check
    db_ok = False
    db_latency_ms = 0.0
    try:
        t0 = time.monotonic()
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
        db_latency_ms = round((time.monotonic() - t0) * 1000, 2)
        db_ok = True
    except Exception as exc:
        db_status = str(exc)
    else:
        db_status = "ok"

    # Redis check
    redis_ok = await CacheService.ping()

    # System metrics
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    total_latency_ms = round((time.monotonic() - start) * 1000, 2)

    status = "ok" if db_ok and redis_ok else "degraded"

    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "latency_ms": total_latency_ms,
        "components": {
            "database": {
                "status": db_status,
                "latency_ms": db_latency_ms,
            },
            "redis": {
                "status": "ok" if redis_ok else "down",
            },
        },
        "system": {
            "cpu_percent": cpu,
            "memory": {
                "total_mb": round(mem.total / 1024 / 1024, 1),
                "used_mb": round(mem.used / 1024 / 1024, 1),
                "percent": mem.percent,
            },
            "disk": {
                "total_gb": round(disk.total / 1024 / 1024 / 1024, 1),
                "used_gb": round(disk.used / 1024 / 1024 / 1024, 1),
                "percent": disk.percent,
            },
        },
    }


@router.get("/ping")
async def ping():
    return {"ping": "pong", "ts": datetime.utcnow().isoformat()}
