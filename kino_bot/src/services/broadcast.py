"""
Broadcast service — sends scheduled mass messages (#15).
Uses asyncio batched sends with configurable delay to respect Telegram limits.
"""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from src.core.config import settings
from src.db.base import AsyncSessionFactory
from src.db.models.broadcast import Broadcast, BroadcastStatus
from src.db.repositories.broadcast_repo import BroadcastRepository
from src.db.repositories.user_repo import UserRepository
from src.services.notification import NotificationService

logger = logging.getLogger(__name__)


class BroadcastService:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._notifier = NotificationService(bot)

    async def execute(self, broadcast: Broadcast) -> None:
        """Execute a broadcast campaign."""
        async with AsyncSessionFactory() as session:
            bc_repo = BroadcastRepository(session)
            user_repo = UserRepository(session)

            user_ids: List[int] = await user_repo.get_all_active_telegram_ids(
                language=broadcast.target_language
            )
            total = len(user_ids)
            await bc_repo.mark_started(broadcast.id, total)
            await session.commit()

        sent = 0
        failed = 0
        batch_size = settings.broadcast_batch_size
        delay = settings.broadcast_delay_ms / 1000.0

        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i : i + batch_size]
            for tg_id in batch:
                try:
                    await self._send_to_user(tg_id, broadcast)
                    sent += 1
                except TelegramForbiddenError:
                    # User blocked the bot
                    failed += 1
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                    try:
                        await self._send_to_user(tg_id, broadcast)
                        sent += 1
                    except Exception:
                        failed += 1
                except Exception as exc:
                    logger.warning("Broadcast send failed for %s: %s", tg_id, exc)
                    failed += 1
                await asyncio.sleep(delay)

        async with AsyncSessionFactory() as session:
            bc_repo = BroadcastRepository(session)
            await bc_repo.mark_finished(broadcast.id, sent, failed)
            await session.commit()

        await self._notifier.broadcast_done(sent, failed)
        logger.info("Broadcast #%d done: sent=%d failed=%d", broadcast.id, sent, failed)

    async def _send_to_user(self, tg_id: int, broadcast: Broadcast) -> None:
        text = broadcast.text
        if broadcast.media_url and broadcast.media_type == "photo":
            await self._bot.send_photo(tg_id, broadcast.media_url, caption=text, parse_mode="HTML")
        elif broadcast.media_url and broadcast.media_type == "video":
            await self._bot.send_video(tg_id, broadcast.media_url, caption=text, parse_mode="HTML")
        else:
            await self._bot.send_message(tg_id, text, parse_mode="HTML")

    async def run_scheduler(self) -> None:
        """Background task: checks every 60s for pending broadcasts."""
        logger.info("Broadcast scheduler started")
        while True:
            try:
                async with AsyncSessionFactory() as session:
                    bc_repo = BroadcastRepository(session)
                    pending = await bc_repo.get_pending()
                    await session.commit()

                for bc in pending:
                    asyncio.create_task(self.execute(bc))

            except Exception as exc:
                logger.error("Broadcast scheduler error: %s", exc)

            await asyncio.sleep(60)
