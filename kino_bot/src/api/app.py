"""
FastAPI application factory — REST API + Swagger + Security (#16, #17, #20).
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.middleware.rate_limit import rate_limit_middleware
from src.api.routers import broadcast, health, movies, stats, users
from src.core.config import settings

logger = logging.getLogger(__name__)


def create_api_app() -> FastAPI:
    app = FastAPI(
        title="Kino Bot Enterprise API",
        description=(
            "## Kino Bot Enterprise REST API\n\n"
            "Authentication: API Key (`X-API-Key` header) or Bearer JWT.\n\n"
            "Rate limit: 60 requests / minute per IP."
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── Security headers ───────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)

    # ── Routers ────────────────────────────────────────────────────────────
    prefix = settings.api_prefix
    app.include_router(health.router)          # /health (no auth)
    app.include_router(movies.router,    prefix=prefix)
    app.include_router(users.router,     prefix=prefix)
    app.include_router(stats.router,     prefix=prefix)
    app.include_router(broadcast.router, prefix=prefix)

    @app.on_event("startup")
    async def on_startup():
        logger.info("FastAPI REST API started on %s:%s", settings.api_host, settings.api_port)

    return app


api_app = create_api_app()
