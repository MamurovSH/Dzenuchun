"""
Analytics service (#22) — daily snapshot builder + reporting.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from src.db.base import AsyncSessionFactory
from src.db.repositories.analytics_repo import AnalyticsRepository
from src.db.repositories.movie_repo import MovieRepository
from src.db.repositories.user_repo import UserRepository
from src.services.cache import CacheService

logger = logging.getLogger(__name__)


class AnalyticsService:

    async def snapshot_today(self) -> None:
        """Called by daily scheduler to persist today's stats."""
        async with AsyncSessionFactory() as session:
            user_repo = UserRepository(session)
            movie_repo = MovieRepository(session)
            analytics_repo = AnalyticsRepository(session)

            total_users = await user_repo.count_total()
            active_users = await user_repo.count_active_today()
            total_movies = await movie_repo.count_total()

            await analytics_repo.upsert_today(
                total_users=total_users,
                active_users=active_users,
                total_movies=total_movies,
            )
            await session.commit()

        await CacheService.invalidate_stats()
        logger.info("Analytics snapshot saved for today")

    async def get_overview(self) -> Dict:
        cached = await CacheService.get_stats("overview")
        if cached:
            return cached

        async with AsyncSessionFactory() as session:
            user_repo = UserRepository(session)
            movie_repo = MovieRepository(session)
            analytics_repo = AnalyticsRepository(session)

            total_users = await user_repo.count_total()
            total_movies = await movie_repo.count_total()
            weekly = await analytics_repo.get_weekly()
            monthly = await analytics_repo.get_monthly()

        data = {
            "total_users": total_users,
            "total_movies": total_movies,
            "weekly": [self._stat_to_dict(s) for s in weekly],
            "monthly": [self._stat_to_dict(s) for s in monthly],
        }
        await CacheService.set_stats("overview", data)
        return data

    async def get_period_stats(self, period: str = "weekly") -> List[Dict]:
        cached = await CacheService.get_stats(period)
        if cached:
            return cached

        async with AsyncSessionFactory() as session:
            analytics_repo = AnalyticsRepository(session)
            if period == "weekly":
                rows = await analytics_repo.get_weekly()
            elif period == "monthly":
                rows = await analytics_repo.get_monthly()
            else:
                rows = await analytics_repo.get_yearly()

        data = [self._stat_to_dict(s) for s in rows]
        await CacheService.set_stats(period, data)
        return data

    @staticmethod
    def _stat_to_dict(s) -> Dict:
        return {
            "date": str(s.stat_date),
            "new_users": s.new_users,
            "active_users": s.active_users,
            "total_users": s.total_users,
            "new_movies": s.new_movies,
            "total_movies": s.total_movies,
            "total_views": s.total_views,
            "total_searches": s.total_searches,
        }

    async def run_scheduler(self) -> None:
        """Background task: saves snapshot every 24h."""
        import asyncio
        logger.info("Analytics scheduler started")
        while True:
            try:
                await self.snapshot_today()
            except Exception as exc:
                logger.error("Analytics scheduler error: %s", exc)
            await asyncio.sleep(86400)  # 24 hours
