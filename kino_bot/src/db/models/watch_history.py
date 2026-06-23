"""
Watch history model — tracks each user's movie views (max 1000 per user).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class WatchHistory(Base):
    __tablename__ = "watch_history"
    __table_args__ = (
        Index("ix_watch_history_user_id", "user_id"),
        Index("ix_watch_history_movie_id", "movie_id"),
        Index("ix_watch_history_watched_at", "watched_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )
    watched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="watch_history")  # type: ignore[name-defined]
    movie: Mapped["Movie"] = relationship("Movie", back_populates="watch_history")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<WatchHistory user={self.user_id} movie={self.movie_id} at={self.watched_at}>"
