"""
Telegram bot application factory — aiogram 3.x.
Registers all routers, middlewares and starts polling/webhook.
"""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from src.bot.handlers import admin, favorites, movies, search, start
from src.bot.middlewares.admin_middleware import AdminMiddleware
from src.bot.middlewares.user_middleware import UserMiddleware
from src.core.config import settings
from src.core.logging import setup_logging
from src.db.base import create_all_tables
from src.services.analytics import AnalyticsService
from src.services.broadcast import BroadcastService
from src.services.cleanup import CleanupService
from src.services.cache import close_redis, get_redis

logger = logging.getLogger(__name__)


async def create_bot() -> tuple[Bot, Dispatcher]:
    setup_logging()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Use Redis FSM storage
    try:
        redis = await get_redis()
        storage = RedisStorage(redis=redis)
        logger.info("Using Redis FSM storage")
    except Exception:
        from aiogram.fsm.storage.memory import MemoryStorage
        storage = MemoryStorage()
        logger.warning("Redis unavailable, falling back to MemoryStorage")

    dp = Dispatcher(storage=storage)

    # ── Middlewares ─────────────────────────────────────────────────────────
    dp.update.outer_middleware(UserMiddleware(bot))
    dp.update.outer_middleware(AdminMiddleware())

    # ── Routers ─────────────────────────────────────────────────────────────
    dp.include_router(start.router)
    dp.include_router(search.router)
    dp.include_router(movies.router)
    dp.include_router(favorites.router)
    dp.include_router(admin.router)

    return bot, dp


async def run_bot() -> None:
    await create_all_tables()
    logger.info("Database tables created/verified")

    bot, dp = await create_bot()

    # Background services
    broadcast_svc = BroadcastService(bot)
    analytics_svc = AnalyticsService()
    cleanup_svc = CleanupService()

    asyncio.create_task(broadcast_svc.run_scheduler())
    asyncio.create_task(analytics_svc.run_scheduler())
    asyncio.create_task(cleanup_svc.run_scheduler())

    logger.info("🎬 Kino Bot Enterprise started!")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await close_redis()
        logger.info("Bot stopped")
