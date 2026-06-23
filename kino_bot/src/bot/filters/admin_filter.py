"""
Filters for admin-only and role-specific access control.
"""
from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from src.core.config import settings
from src.db.models.admin import Admin, AdminRole, ROLE_PERMISSIONS


class IsAdmin(BaseFilter):
    """Passes if the user is in the admin list (any role)."""
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        uid = event.from_user.id if event.from_user else None
        return uid in settings.all_admin_ids


class IsSuperAdmin(BaseFilter):
    """Passes only for super admin."""
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        uid = event.from_user.id if event.from_user else None
        return uid == settings.super_admin_id


class HasPermission(BaseFilter):
    """Passes if the attached Admin object has the required permission."""
    def __init__(self, permission: str) -> None:
        self.permission = permission

    async def __call__(self, event: Message | CallbackQuery, admin: Admin | None = None) -> bool:
        if not admin:
            return False
        return admin.has_permission(self.permission)
