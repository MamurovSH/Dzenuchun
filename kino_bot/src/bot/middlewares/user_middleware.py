"""
User loader middleware — ensures every update has a valid User in data dict.
Also handles blocked/banned/muted status checks.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, Message, CallbackQuery

from src.db.base import AsyncSessionFactory
from src.db.models.user import UserStatus
from src.db.repositories.user_repo import UserRepository
from src.services.notification import NotificationService
from src.utils.i18n import t

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    def __init__(self, bot=None) -> None:
        self._bot = bot

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = None
        if isinstance(event, (Message, CallbackQuery)):
            tg_user = event.from_user

        if not tg_user:
            return await handler(event, data)

        async with AsyncSessionFactory() as session:
            user_repo = UserRepository(session)
            user, is_new = await user_repo.get_or_create(
                telegram_id=tg_user.id,
                first_name=tg_user.first_name or "",
                last_name=tg_user.last_name,
                username=tg_user.username,
            )

            # Handle moderation statuses
            if user.status == UserStatus.BANNED:
                msg = t("user_banned", user.language.value, reason=user.ban_reason or "")
                if isinstance(event, Message):
                    await event.answer(msg)
                elif isinstance(event, CallbackQuery):
                    await event.answer(msg, show_alert=True)
                return

            if user.status == UserStatus.TEMP_BANNED:
                if user.ban_until and user.ban_until > datetime.now(timezone.utc):
                    msg = t("user_temp_banned", user.language.value,
                            until=user.ban_until.strftime("%Y-%m-%d %H:%M"))
                    if isinstance(event, Message):
                        await event.answer(msg)
                    elif isinstance(event, CallbackQuery):
                        await event.answer(msg, show_alert=True)
                    return

            if user.status == UserStatus.BLOCKED:
                msg = t("user_blocked", user.language.value, reason=user.ban_reason or "")
                if isinstance(event, Message):
                    await event.answer(msg)
                elif isinstance(event, CallbackQuery):
                    await event.answer(msg, show_alert=True)
                return

            await user_repo.update_last_active(tg_user.id)
            await session.commit()

            data["user"] = user
            data["lang"] = user.language.value
            data["is_new_user"] = is_new
            data["session"] = session

        # Notify admins about new user
        if is_new and self._bot:
            try:
                notifier = NotificationService(self._bot)
                await notifier.new_user(
                    name=tg_user.full_name,
                    tg_id=tg_user.id,
                    lang=user.language.value,
                )
            except Exception as exc:
                logger.warning("New user notification failed: %s", exc)

        return await handler(event, data)
