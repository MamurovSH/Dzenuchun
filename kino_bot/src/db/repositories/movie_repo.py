"""
Movie repository — all DB operations for Movie model.
Tasks #4 (Smart Search), #5 (Filter), #6 (Top), #7 (Recent) live here.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select, update, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.movie import Movie
from src.core.config import settings


class MovieRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    # ── CRUD ───────────────────────────────────────────────────────────────

    async def get_by_id(self, movie_id: int) -> Optional[Movie]:
        result = await self._s.execute(
            select(Movie).where(Movie.id == movie_id, Movie.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Movie]:
        result = await self._s.execute(
            select(Movie).where(
                func.upper(Movie.code) == code.upper().strip(),
                Movie.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 0, per_page: int = None) -> Tuple[List[Movie], int]:
        per_page = per_page or settings.movies_per_page
        count_q = await self._s.execute(
            select(func.count()).select_from(Movie).where(Movie.is_active == True)
        )
        total = count_q.scalar_one()
        result = await self._s.execute(
            select(Movie)
            .where(Movie.is_active == True)
            .order_by(desc(Movie.created_at))
            .offset(page * per_page)
            .limit(per_page)
        )
        return result.scalars().all(), total

    async def create(self, **kwargs) -> Movie:
        movie = Movie(**kwargs)
        self._s.add(movie)
        await self._s.flush()
        return movie

    async def update(self, movie_id: int, **kwargs) -> Optional[Movie]:
        await self._s.execute(
            update(Movie).where(Movie.id == movie_id).values(**kwargs)
        )
        return await self.get_by_id(movie_id)

    async def delete(self, movie_id: int) -> bool:
        movie = await self.get_by_id(movie_id)
        if not movie:
            return False
        await self._s.delete(movie)
        return True

    async def soft_delete(self, movie_id: int) -> bool:
        result = await self._s.execute(
            update(Movie)
            .where(Movie.id == movie_id)
            .values(is_active=False)
        )
        return result.rowcount > 0

    # ── SMART SEARCH (#4) ──────────────────────────────────────────────────
    # Searches: code, title (UZ/RU/EN/original), partial name, tags

    async def smart_search(
        self,
        query: str,
        page: int = 0,
        per_page: int = None,
    ) -> Tuple[List[Movie], int]:
        per_page = per_page or settings.search_max_results
        q = query.strip().lower()

        # Exact code match first
        if re.match(r"^[a-z]{2,6}\d{3,}$", q, re.IGNORECASE):
            movie = await self.get_by_code(q)
            if movie:
                return [movie], 1

        like_q = f"%{q}%"
        condition = and_(
            Movie.is_active == True,
            or_(
                func.lower(Movie.code).like(like_q),
                func.lower(Movie.title).like(like_q),
                func.lower(Movie.title_uz).like(like_q),
                func.lower(Movie.title_ru).like(like_q),
                func.lower(Movie.title_en).like(like_q),
                func.lower(Movie.director).like(like_q),
                # Tags array contains match
                Movie.tags.any(func.lower(func.cast(func.unnest(Movie.tags), type_=Movie.tags.type.item_type)).like(like_q)),
            ),
        )

        count_q = await self._s.execute(
            select(func.count()).select_from(Movie).where(condition)
        )
        total = count_q.scalar_one()

        result = await self._s.execute(
            select(Movie)
            .where(condition)
            .order_by(desc(Movie.rating), desc(Movie.view_count))
            .offset(page * per_page)
            .limit(per_page)
        )
        return result.scalars().all(), total

    # ── FILTER SEARCH (#5) ─────────────────────────────────────────────────

    async def filter_movies(
        self,
        genre: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        country: Optional[str] = None,
        language: Optional[str] = None,
        min_rating: Optional[float] = None,
        page: int = 0,
        per_page: int = None,
    ) -> Tuple[List[Movie], int]:
        per_page = per_page or settings.movies_per_page
        conditions = [Movie.is_active == True]

        if genre:
            conditions.append(Movie.genres.any(genre))
        if year_from:
            conditions.append(Movie.year >= year_from)
        if year_to:
            conditions.append(Movie.year <= year_to)
        if country:
            conditions.append(func.lower(Movie.country).like(f"%{country.lower()}%"))
        if language:
            conditions.append(func.lower(Movie.language).like(f"%{language.lower()}%"))
        if min_rating is not None:
            conditions.append(Movie.rating >= min_rating)

        where_clause = and_(*conditions)

        count_q = await self._s.execute(
            select(func.count()).select_from(Movie).where(where_clause)
        )
        total = count_q.scalar_one()

        result = await self._s.execute(
            select(Movie)
            .where(where_clause)
            .order_by(desc(Movie.rating), desc(Movie.year))
            .offset(page * per_page)
            .limit(per_page)
        )
        return result.scalars().all(), total

    # ── TOP MOVIES (#6) ────────────────────────────────────────────────────

    async def get_top_movies(
        self,
        period: str = "alltime",  # weekly | monthly | yearly | alltime
        limit: int = 10,
    ) -> List[Movie]:
        """Return top N movies ordered by view count for the given period."""
        period_col_map = {
            "weekly": Movie.weekly_views,
            "monthly": Movie.monthly_views,
            "yearly": Movie.yearly_views,
            "alltime": Movie.view_count,
        }
        order_col = period_col_map.get(period, Movie.view_count)

        result = await self._s.execute(
            select(Movie)
            .where(Movie.is_active == True)
            .order_by(desc(order_col), desc(Movie.rating))
            .limit(limit)
        )
        return result.scalars().all()

    # ── RECENT MOVIES (#7) ─────────────────────────────────────────────────

    async def get_recent(
        self,
        page: int = 0,
        per_page: int = None,
    ) -> Tuple[List[Movie], int]:
        per_page = per_page or settings.movies_per_page
        count_q = await self._s.execute(
            select(func.count()).select_from(Movie).where(Movie.is_active == True)
        )
        total = count_q.scalar_one()
        result = await self._s.execute(
            select(Movie)
            .where(Movie.is_active == True)
            .order_by(desc(Movie.created_at))
            .offset(page * per_page)
            .limit(per_page)
        )
        return result.scalars().all(), total

    # ── VIEW TRACKING ──────────────────────────────────────────────────────

    async def increment_view(self, movie_id: int) -> None:
        await self._s.execute(
            update(Movie)
            .where(Movie.id == movie_id)
            .values(
                view_count=Movie.view_count + 1,
                weekly_views=Movie.weekly_views + 1,
                monthly_views=Movie.monthly_views + 1,
                yearly_views=Movie.yearly_views + 1,
            )
        )

    async def reset_period_views(self, period: str) -> None:
        """Called by scheduler to reset weekly/monthly/yearly counters."""
        col_map = {
            "weekly": {"weekly_views": 0},
            "monthly": {"monthly_views": 0},
            "yearly": {"yearly_views": 0},
        }
        values = col_map.get(period)
        if values:
            await self._s.execute(update(Movie).values(**values))

    # ── DISTINCT FILTER VALUES ─────────────────────────────────────────────

    async def get_distinct_countries(self) -> List[str]:
        result = await self._s.execute(
            select(Movie.country)
            .where(Movie.is_active == True, Movie.country != None)
            .distinct()
            .order_by(Movie.country)
        )
        return [r[0] for r in result.all() if r[0]]

    async def get_distinct_languages(self) -> List[str]:
        result = await self._s.execute(
            select(Movie.language)
            .where(Movie.is_active == True, Movie.language != None)
            .distinct()
            .order_by(Movie.language)
        )
        return [r[0] for r in result.all() if r[0]]

    async def get_all_genres(self) -> List[str]:
        result = await self._s.execute(
            select(func.unnest(Movie.genres).label("genre"))
            .where(Movie.is_active == True)
            .distinct()
            .order_by("genre")
        )
        return [r[0] for r in result.all() if r[0]]

    async def count_total(self) -> int:
        result = await self._s.execute(
            select(func.count()).select_from(Movie).where(Movie.is_active == True)
        )
        return result.scalar_one()
