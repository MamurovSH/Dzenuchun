"""
User repository — CRUD + moderation operations.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User, UserLanguage, UserStatus
from src.core.config import settings


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_telegram_id(self, tg_id: int) -> Optional[User]:
        result = await self._s.execute(
            select(User).where(User.telegram_id == tg_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self._s.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        language: str = "uz",
    ) -> Tuple[User, bool]:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            # Update profile info silently
            await self._s.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    last_active=datetime.now(timezone.utc),
                )
            )
            return user, False

        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language=UserLanguage(language) if language in ("uz", "ru", "en") else UserLanguage.UZ,
        )
        self._s.add(user)
        await self._s.flush()
        return user, True

    async def set_language(self, telegram_id: int, lang: str) -> None:
        await self._s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(language=UserLanguage(lang))
        )

    async def update_last_active(self, telegram_id: int) -> None:
        await self._s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(last_active=datetime.now(timezone.utc))
        )

    async def increment_searches(self, telegram_id: int) -> None:
        await self._s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(total_searches=User.total_searches + 1)
        )

    async def increment_views(self, telegram_id: int) -> None:
        await self._s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(total_views=User.total_views + 1)
        )

    # ── MODERATION (#14) ──────────────────────────────────────────────────

    async def block_user(self, telegram_id: int, reason: str = "") -> bool:
        result = await self._s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(status=UserStatus.BLOCKED, ban_reason=reason)
        )
        return result.rowcount > 0

    async def unblock_user(self, telegram_id: int) -> bool:
        result = await self._s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(status=UserStatus.ACTIVE, ban_reason=None, ban_until=None)
        )
        return result.rowcount > 0

    async def mute_user(self, telegram_id: int, until: datetime) -> bool:
        result = await self._s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(status=UserStatus.MUTED, muted_until=until)
        )
        return result.rowcount > 0

    async def warn_user(self, telegram_id: int) -> int:
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            return 0
        new_count = user.warn_count + 1
        await self._s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(warn_count=new_count)
        )
        return new_count

    async def ban_user(self, telegram_id: int, reason: str = "") -> bool:
        result = await self._s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(status=UserStatus.BANNED, ban_reason=reason)
        )
        return result.rowcount > 0

    async def temp_ban_user(self, telegram_id: int, until: datetime, reason: str = "") -> bool:
        result = await self._s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(status=UserStatus.TEMP_BANNED, ban_until=until, ban_reason=reason)
        )
        return result.rowcount > 0

    # ── LISTING ───────────────────────────────────────────────────────────

    async def get_all_active_telegram_ids(self, language: Optional[str] = None) -> List[int]:
        q = select(User.telegram_id).where(User.status == UserStatus.ACTIVE)
        if language:
            q = q.where(User.language == UserLanguage(language))
        result = await self._s.execute(q)
        return [r[0] for r in result.all()]

    async def get_page(
        self,
        page: int = 0,
        per_page: int = None,
        status: Optional[UserStatus] = None,
    ) -> Tuple[List[User], int]:
        per_page = per_page or settings.users_per_page
        conditions = []
        if status:
            conditions.append(User.status == status)

        base_q = select(User)
        count_q = select(func.count()).select_from(User)
        if conditions:
            from sqlalchemy import and_
            base_q = base_q.where(and_(*conditions))
            count_q = count_q.where(and_(*conditions))

        total = (await self._s.execute(count_q)).scalar_one()
        result = await self._s.execute(
            base_q.order_by(desc(User.created_at)).offset(page * per_page).limit(per_page)
        )
        return result.scalars().all(), total

    async def count_total(self) -> int:
        result = await self._s.execute(select(func.count()).select_from(User))
        return result.scalar_one()

    async def count_active_today(self) -> int:
        from datetime import date
        today = datetime.now(timezone.utc).date()
        result = await self._s.execute(
            select(func.count()).select_from(User).where(
                func.date(User.last_active) == today
            )
        )
        return result.scalar_one()
