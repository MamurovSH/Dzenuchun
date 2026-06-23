"""
Daily statistics snapshot model for analytics charts.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class DailyStats(Base):
    __tablename__ = "daily_stats"
    __table_args__ = (
        UniqueConstraint("stat_date", name="uq_daily_stats_date"),
        Index("ix_daily_stats_date", "stat_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stat_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)

    # User metrics
    new_users: Mapped[int] = mapped_column(Integer, default=0)
    active_users: Mapped[int] = mapped_column(Integer, default=0)
    total_users: Mapped[int] = mapped_column(Integer, default=0)

    # Movie metrics
    new_movies: Mapped[int] = mapped_column(Integer, default=0)
    total_movies: Mapped[int] = mapped_column(Integer, default=0)
    total_views: Mapped[int] = mapped_column(Integer, default=0)

    # Search metrics
    total_searches: Mapped[int] = mapped_column(Integer, default=0)

    # Broadcast metrics
    broadcasts_sent: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<DailyStats date={self.stat_date} users={self.active_users}>"
