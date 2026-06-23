"""
Admin model with role-based permission system.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"


# Permission matrix: role → set of allowed actions
ROLE_PERMISSIONS: dict[AdminRole, set[str]] = {
    AdminRole.SUPER_ADMIN: {
        "manage_admins", "manage_movies", "manage_users",
        "view_stats", "export_data", "broadcast",
        "delete_movie", "ban_user", "edit_settings",
        "view_logs", "manage_api_keys",
    },
    AdminRole.ADMIN: {
        "manage_movies", "manage_users", "view_stats",
        "export_data", "broadcast", "delete_movie",
        "ban_user", "view_logs",
    },
    AdminRole.MODERATOR: {
        "manage_movies", "manage_users", "view_stats",
        "ban_user", "view_logs",
    },
    AdminRole.SUPPORT: {
        "manage_users", "view_stats", "view_logs",
    },
}


class Admin(Base):
    __tablename__ = "admins"
    __table_args__ = (
        Index("ix_admins_telegram_id", "telegram_id", unique=True),
        Index("ix_admins_role", "role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    role: Mapped[AdminRole] = mapped_column(
        Enum(AdminRole), default=AdminRole.SUPPORT, nullable=False
    )

    # 2FA
    totp_secret: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_2fa_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Added by
    added_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def has_permission(self, perm: str) -> bool:
        return perm in ROLE_PERMISSIONS.get(self.role, set())

    def __repr__(self) -> str:
        return f"<Admin id={self.id} tg={self.telegram_id} role={self.role}>"
