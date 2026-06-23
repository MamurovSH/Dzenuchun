"""
User model — every Telegram user who starts the bot.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class UserLanguage(str, enum.Enum):
    UZ = "uz"
    RU = "ru"
    EN = "en"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    MUTED = "muted"
    BANNED = "banned"
    TEMP_BANNED = "temp_banned"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_telegram_id", "telegram_id", unique=True),
        Index("ix_users_username", "username"),
        Index("ix_users_status", "status"),
        Index("ix_users_language", "language"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    last_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    language: Mapped[UserLanguage] = mapped_column(
        Enum(UserLanguage), default=UserLanguage.UZ, nullable=False
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False
    )
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)

    # Moderation
    warn_count: Mapped[int] = mapped_column(Integer, default=0)
    ban_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ban_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    muted_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Activity tracking
    last_active: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_searches: Mapped[int] = mapped_column(Integer, default=0)
    total_views: Mapped[int] = mapped_column(Integer, default=0)

    # Channel subscription
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    favorites: Mapped[List["Favorite"]] = relationship(  # type: ignore[name-defined]
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )
    watch_history: Mapped[List["WatchHistory"]] = relationship(  # type: ignore[name-defined]
        "WatchHistory", back_populates="user", cascade="all, delete-orphan",
        order_by="WatchHistory.watched_at.desc()",
    )

    @property
    def full_name(self) -> str:
        parts = [self.first_name or ""]
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(p for p in parts if p).strip() or "Unknown"

    @property
    def mention(self) -> str:
        if self.username:
            return f"@{self.username}"
        return f'<a href="tg://user?id={self.telegram_id}">{self.full_name}</a>'

    def __repr__(self) -> str:
        return f"<User id={self.id} tg={self.telegram_id} name={self.full_name!r}>"
