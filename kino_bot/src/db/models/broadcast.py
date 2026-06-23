"""
Broadcast models — scheduled message campaigns.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class BroadcastStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Broadcast(Base):
    __tablename__ = "broadcasts"
    __table_args__ = (
        Index("ix_broadcasts_status", "status"),
        Index("ix_broadcasts_scheduled_at", "scheduled_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    media_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # photo/video/doc

    status: Mapped[BroadcastStatus] = mapped_column(
        Enum(BroadcastStatus), default=BroadcastStatus.DRAFT, nullable=False
    )
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Target filters (JSON-serialised query or None = all users)
    target_language: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)

    # Statistics
    total_recipients: Mapped[int] = mapped_column(Integer, default=0)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)

    # Admin who created it
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    recipients: Mapped[list["BroadcastRecipient"]] = relationship(
        "BroadcastRecipient", back_populates="broadcast", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Broadcast id={self.id} status={self.status} title={self.title!r}>"


class BroadcastRecipient(Base):
    __tablename__ = "broadcast_recipients"
    __table_args__ = (
        Index("ix_bcast_recipients_broadcast_id", "broadcast_id"),
        Index("ix_bcast_recipients_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    broadcast_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("broadcasts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_failed: Mapped[bool] = mapped_column(Boolean, default=False)
    error_msg: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    broadcast: Mapped["Broadcast"] = relationship("Broadcast", back_populates="recipients")
