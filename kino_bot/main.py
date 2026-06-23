#!/usr/bin/env python3
"""
Main entry point — runs bot + REST API + Dashboard concurrently.
"""
from __future__ import annotations

import asyncio
import logging
import sys

import uvicorn

from src.core.config import settings
from src.core.logging import setup_logging


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Kino Bot Enterprise v2.0.0")

    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode == "bot":
        from src.bot.app import run_bot
        await run_bot()

    elif mode == "api":
        from src.api.app import api_app
        config = uvicorn.Config(
            api_app,
            host=settings.api_host,
            port=settings.api_port,
            log_level=settings.log_level.lower(),
        )
        server = uvicorn.Server(config)
        await server.serve()

    elif mode == "dashboard":
        from src.dashboard.app import dashboard_app
        config = uvicorn.Config(
            dashboard_app,
            host=settings.dashboard_host,
            port=settings.dashboard_port,
            log_level=settings.log_level.lower(),
        )
        server = uvicorn.Server(config)
        await server.serve()

    else:  # "all" — run everything concurrently
        from src.api.app import api_app
        from src.bot.app import run_bot
        from src.dashboard.app import dashboard_app

        api_config = uvicorn.Config(
            api_app,
            host=settings.api_host,
            port=settings.api_port,
            log_level=settings.log_level.lower(),
        )
        dash_config = uvicorn.Config(
            dashboard_app,
            host=settings.dashboard_host,
            port=settings.dashboard_port,
            log_level=settings.log_level.lower(),
        )

        api_server = uvicorn.Server(api_config)
        dash_server = uvicorn.Server(dash_config)

        await asyncio.gather(
            run_bot(),
            api_server.serve(),
            dash_server.serve(),
        )


if __name__ == "__main__":
    asyncio.run(main())
