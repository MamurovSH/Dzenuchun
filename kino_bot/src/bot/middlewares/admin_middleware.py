"""
Admin authentication middleware — attaches Admin object to data for admin routes.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from src.core.config import settings
from src.db.base import AsyncSessionFactory
from src.db.repositories.admin_repo import AdminRepository


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = None
        if isinstance(event, (Message, CallbackQuery)):
            tg_user = event.from_user

        if tg_user and tg_user.id in settings.all_admin_ids:
            async with AsyncSessionFactory() as session:
                admin_repo = AdminRepository(session)
                admin = await admin_repo.get_by_telegram_id(tg_user.id)
                data["admin"] = admin
        else:
            data["admin"] = None

        return await handler(event, data)
