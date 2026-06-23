"""
Favorite model — user's saved movies list.
"""
from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_favorite_user_movie"),
        Index("ix_favorites_user_id", "user_id"),
        Index("ix_favorites_movie_id", "movie_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="favorites")  # type: ignore[name-defined]
    movie: Mapped["Movie"] = relationship("Movie", back_populates="favorites")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<Favorite user={self.user_id} movie={self.movie_id}>"
