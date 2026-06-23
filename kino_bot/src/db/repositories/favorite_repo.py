"""
Favorite repository — user's saved movies list (#8).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.favorite import Favorite
from src.db.models.movie import Movie
from src.core.config import settings


class FavoriteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, user_id: int, movie_id: int) -> Tuple[Favorite, bool]:
        """Add movie to favorites. Returns (fav, created)."""
        existing = await self._s.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.movie_id == movie_id,
            )
        )
        fav = existing.scalar_one_or_none()
        if fav:
            return fav, False
        fav = Favorite(user_id=user_id, movie_id=movie_id)
        self._s.add(fav)
        await self._s.flush()
        return fav, True

    async def remove(self, user_id: int, movie_id: int) -> bool:
        result = await self._s.execute(
            delete(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.movie_id == movie_id,
            )
        )
        return result.rowcount > 0

    async def is_favorite(self, user_id: int, movie_id: int) -> bool:
        result = await self._s.execute(
            select(Favorite.id).where(
                Favorite.user_id == user_id,
                Favorite.movie_id == movie_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_user_favorites(
        self,
        user_id: int,
        page: int = 0,
        per_page: int = None,
    ) -> Tuple[List[Movie], int]:
        per_page = per_page or settings.movies_per_page
        count_q = await self._s.execute(
            select(func.count()).select_from(Favorite).where(Favorite.user_id == user_id)
        )
        total = count_q.scalar_one()

        result = await self._s.execute(
            select(Movie)
            .join(Favorite, Favorite.movie_id == Movie.id)
            .where(Favorite.user_id == user_id, Movie.is_active == True)
            .order_by(Favorite.created_at.desc())
            .offset(page * per_page)
            .limit(per_page)
        )
        return result.scalars().all(), total
