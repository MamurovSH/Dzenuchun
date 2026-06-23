"""
Admin notification service (#21).
Sends alerts to all active admins for key system events.
"""
from __future__ import annotations

import logging
from typing import Optional

from aiogram import Bot

from src.core.config import settings
from src.utils.i18n import t

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def _send(self, text: str) -> None:
        for admin_id in settings.all_admin_ids:
            try:
                await self._bot.send_message(admin_id, text, parse_mode="HTML")
            except Exception as exc:
                logger.warning("Failed to notify admin %s: %s", admin_id, exc)

    async def new_user(self, name: str, tg_id: int, lang: str) -> None:
        if not settings.enable_notifications:
            return
        await self._send(t("notify_new_user", "uz", name=name, id=tg_id, lang=lang))

    async def new_movie(self, title: str, code: str) -> None:
        if not settings.enable_notifications:
            return
        await self._send(t("notify_new_movie", "uz", title=title, code=code))

    async def broadcast_done(self, sent: int, failed: int) -> None:
        if not settings.enable_notifications:
            return
        await self._send(t("notify_broadcast_done", "uz", sent=sent, failed=failed))

    async def server_error(self, error: str) -> None:
        if not settings.enable_notifications:
            return
        await self._send(t("notify_server_error", "uz", error=error[:500]))

    async def custom(self, text: str) -> None:
        await self._send(text)
