"""
Watch history repository (#9) — max 1000 entries per user.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import delete, func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.watch_history import WatchHistory
from src.db.models.movie import Movie
from src.core.config import settings


class HistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, user_id: int, movie_id: int) -> None:
        """Record a view. Purges oldest entries beyond the limit."""
        entry = WatchHistory(
            user_id=user_id,
            movie_id=movie_id,
            watched_at=datetime.now(timezone.utc),
        )
        self._s.add(entry)
        await self._s.flush()
        await self._purge_old(user_id)

    async def _purge_old(self, user_id: int) -> None:
        limit = settings.watch_history_limit
        count_q = await self._s.execute(
            select(func.count())
            .select_from(WatchHistory)
            .where(WatchHistory.user_id == user_id)
        )
        total = count_q.scalar_one()
        if total > limit:
            excess = total - limit
            oldest = await self._s.execute(
                select(WatchHistory.id)
                .where(WatchHistory.user_id == user_id)
                .order_by(WatchHistory.watched_at.asc())
                .limit(excess)
            )
            ids = [r[0] for r in oldest.all()]
            if ids:
                await self._s.execute(
                    delete(WatchHistory).where(WatchHistory.id.in_(ids))
                )

    async def get_user_history(
        self,
        user_id: int,
        page: int = 0,
        per_page: int = None,
    ) -> Tuple[List[Movie], int]:
        per_page = per_page or settings.movies_per_page
        count_q = await self._s.execute(
            select(func.count())
            .select_from(WatchHistory)
            .where(WatchHistory.user_id == user_id)
        )
        total = count_q.scalar_one()

        result = await self._s.execute(
            select(Movie)
            .join(WatchHistory, WatchHistory.movie_id == Movie.id)
            .where(WatchHistory.user_id == user_id)
            .order_by(WatchHistory.watched_at.desc())
            .offset(page * per_page)
            .limit(per_page)
        )
        return result.scalars().all(), total

    async def clear_user_history(self, user_id: int) -> int:
        result = await self._s.execute(
            delete(WatchHistory).where(WatchHistory.user_id == user_id)
        )
        return result.rowcount
