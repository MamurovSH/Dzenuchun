"""
Broadcast repository (#15).
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.broadcast import Broadcast, BroadcastRecipient, BroadcastStatus


class BroadcastRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(
        self,
        title: str,
        text: str,
        created_by: int,
        scheduled_at: Optional[datetime] = None,
        target_language: Optional[str] = None,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None,
    ) -> Broadcast:
        bc = Broadcast(
            title=title,
            text=text,
            created_by=created_by,
            scheduled_at=scheduled_at,
            target_language=target_language,
            media_url=media_url,
            media_type=media_type,
            status=BroadcastStatus.SCHEDULED if scheduled_at else BroadcastStatus.DRAFT,
        )
        self._s.add(bc)
        await self._s.flush()
        return bc

    async def get_by_id(self, bc_id: int) -> Optional[Broadcast]:
        result = await self._s.execute(select(Broadcast).where(Broadcast.id == bc_id))
        return result.scalar_one_or_none()

    async def get_pending(self) -> List[Broadcast]:
        """Returns broadcasts ready to be sent (scheduled_at <= now)."""
        now = datetime.utcnow()
        result = await self._s.execute(
            select(Broadcast).where(
                Broadcast.status == BroadcastStatus.SCHEDULED,
                Broadcast.scheduled_at <= now,
            )
        )
        return result.scalars().all()

    async def set_status(self, bc_id: int, status: BroadcastStatus) -> None:
        await self._s.execute(
            update(Broadcast).where(Broadcast.id == bc_id).values(status=status)
        )

    async def update_stats(self, bc_id: int, sent: int, failed: int) -> None:
        await self._s.execute(
            update(Broadcast)
            .where(Broadcast.id == bc_id)
            .values(sent_count=sent, failed_count=failed)
        )

    async def mark_started(self, bc_id: int, total: int) -> None:
        await self._s.execute(
            update(Broadcast)
            .where(Broadcast.id == bc_id)
            .values(
                status=BroadcastStatus.SENDING,
                started_at=datetime.utcnow(),
                total_recipients=total,
            )
        )

    async def mark_finished(self, bc_id: int, sent: int, failed: int) -> None:
        await self._s.execute(
            update(Broadcast)
            .where(Broadcast.id == bc_id)
            .values(
                status=BroadcastStatus.COMPLETED,
                finished_at=datetime.utcnow(),
                sent_count=sent,
                failed_count=failed,
            )
        )

    async def cancel(self, bc_id: int) -> bool:
        result = await self._s.execute(
            update(Broadcast)
            .where(Broadcast.id == bc_id, Broadcast.status.in_([
                BroadcastStatus.DRAFT, BroadcastStatus.SCHEDULED
            ]))
            .values(status=BroadcastStatus.CANCELLED)
        )
        return result.rowcount > 0

    async def list_all(self, limit: int = 50) -> List[Broadcast]:
        result = await self._s.execute(
            select(Broadcast).order_by(Broadcast.created_at.desc()).limit(limit)
        )
        return result.scalars().all()
