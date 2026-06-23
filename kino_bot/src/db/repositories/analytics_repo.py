"""
Analytics repository (#22) — daily stats snapshots.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.analytics import DailyStats


class AnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def upsert_today(self, **kwargs) -> DailyStats:
        today = datetime.utcnow().date()
        stmt = (
            pg_insert(DailyStats)
            .values(stat_date=today, **kwargs)
            .on_conflict_do_update(
                index_elements=["stat_date"],
                set_={k: v for k, v in kwargs.items()},
            )
            .returning(DailyStats)
        )
        result = await self._s.execute(stmt)
        return result.scalar_one()

    async def get_by_date(self, stat_date: date) -> Optional[DailyStats]:
        result = await self._s.execute(
            select(DailyStats).where(DailyStats.stat_date == stat_date)
        )
        return result.scalar_one_or_none()

    async def get_range(self, days: int = 30) -> List[DailyStats]:
        since = datetime.utcnow().date() - timedelta(days=days)
        result = await self._s.execute(
            select(DailyStats)
            .where(DailyStats.stat_date >= since)
            .order_by(DailyStats.stat_date.asc())
        )
        return result.scalars().all()

    async def get_weekly(self) -> List[DailyStats]:
        return await self.get_range(7)

    async def get_monthly(self) -> List[DailyStats]:
        return await self.get_range(30)

    async def get_yearly(self) -> List[DailyStats]:
        return await self.get_range(365)
