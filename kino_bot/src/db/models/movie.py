"""
Movie model — the central entity of the bot.
Supports multi-language titles, full-text search indexes, and view tracking.
"""
from __future__ import annotations

import enum
from typing import List, Optional

from sqlalchemy import (
    ARRAY, Boolean, Float, Index, Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        Index("ix_movies_code", "code", unique=True),
        Index("ix_movies_year", "year"),
        Index("ix_movies_rating", "rating"),
        Index("ix_movies_view_count", "view_count"),
        Index("ix_movies_is_active", "is_active"),
        # Partial full-text index for active movies
        Index(
            "ix_movies_fts_uz",
            func.to_tsvector("simple", func.coalesce("title_uz", "")),
            postgresql_using="gin",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Unique short code (e.g. "TIT001", "AVG001")
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Multi-language titles
    title: Mapped[str] = mapped_column(String(256), nullable=False)          # Original
    title_uz: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)   # Uzbek
    title_ru: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)   # Russian
    title_en: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)   # English

    # Metadata
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    genres: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(64)), nullable=True)
    director: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    cast: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(128)), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    duration: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    # Rating and metrics
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    imdb_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    kinopoisk_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Descriptions (multi-language)
    description_uz: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Media
    poster_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    trailer_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    watch_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)  # Telegram file_id

    # Searchable tags
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(64)), nullable=True)

    # View statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    weekly_views: Mapped[int] = mapped_column(Integer, default=0)
    monthly_views: Mapped[int] = mapped_column(Integer, default=0)
    yearly_views: Mapped[int] = mapped_column(Integer, default=0)

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    favorites: Mapped[List["Favorite"]] = relationship(  # type: ignore[name-defined]
        "Favorite", back_populates="movie", cascade="all, delete-orphan"
    )
    watch_history: Mapped[List["WatchHistory"]] = relationship(  # type: ignore[name-defined]
        "WatchHistory", back_populates="movie", cascade="all, delete-orphan"
    )

    def get_title(self, lang: str = "uz") -> str:
        """Return best available title for given language."""
        mapping = {
            "uz": self.title_uz or self.title_en or self.title,
            "ru": self.title_ru or self.title_en or self.title,
            "en": self.title_en or self.title,
        }
        return mapping.get(lang, self.title) or self.title

    def get_description(self, lang: str = "uz") -> str:
        mapping = {
            "uz": self.description_uz or self.description_ru or self.description_en or "",
            "ru": self.description_ru or self.description_en or "",
            "en": self.description_en or "",
        }
        return mapping.get(lang, "") or ""

    def __repr__(self) -> str:
        return f"<Movie id={self.id} code={self.code!r} title={self.title!r}>"
