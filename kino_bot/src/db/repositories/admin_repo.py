"""
Admin repository — CRUD + role management.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.admin import Admin, AdminRole


class AdminRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_telegram_id(self, tg_id: int) -> Optional[Admin]:
        result = await self._s.execute(
            select(Admin).where(Admin.telegram_id == tg_id, Admin.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, admin_id: int) -> Optional[Admin]:
        result = await self._s.execute(select(Admin).where(Admin.id == admin_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        full_name: str,
        role: AdminRole,
        username: Optional[str] = None,
        added_by: Optional[int] = None,
    ) -> Admin:
        admin = Admin(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
            role=role,
            added_by_id=added_by,
        )
        self._s.add(admin)
        await self._s.flush()
        return admin

    async def update_role(self, telegram_id: int, role: AdminRole) -> bool:
        result = await self._s.execute(
            update(Admin)
            .where(Admin.telegram_id == telegram_id)
            .values(role=role)
        )
        return result.rowcount > 0

    async def deactivate(self, telegram_id: int) -> bool:
        result = await self._s.execute(
            update(Admin)
            .where(Admin.telegram_id == telegram_id)
            .values(is_active=False)
        )
        return result.rowcount > 0

    async def set_totp_secret(self, telegram_id: int, secret: str) -> None:
        await self._s.execute(
            update(Admin)
            .where(Admin.telegram_id == telegram_id)
            .values(totp_secret=secret, totp_enabled=True)
        )

    async def set_2fa_verified(self, telegram_id: int, verified: bool) -> None:
        await self._s.execute(
            update(Admin)
            .where(Admin.telegram_id == telegram_id)
            .values(is_2fa_verified=verified)
        )

    async def update_last_login(self, telegram_id: int) -> None:
        await self._s.execute(
            update(Admin)
            .where(Admin.telegram_id == telegram_id)
            .values(last_login=datetime.now(timezone.utc))
        )

    async def get_all(self) -> List[Admin]:
        result = await self._s.execute(
            select(Admin).where(Admin.is_active == True).order_by(Admin.role)
        )
        return result.scalars().all()

    async def exists(self, telegram_id: int) -> bool:
        result = await self._s.execute(
            select(Admin.id).where(Admin.telegram_id == telegram_id, Admin.is_active == True)
        )
        return result.scalar_one_or_none() is not None
