"""
Auto cleanup service (#23) — purges old logs, expired sessions, backups.
"""
from __future__ import annotations

import asyncio
import glob
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete, func, select, update

from src.core.config import settings
from src.db.base import AsyncSessionFactory
from src.db.models.user import User, UserStatus
from src.services.cache import CacheService

logger = logging.getLogger(__name__)


class CleanupService:

    async def run_all(self) -> None:
        logger.info("Running cleanup tasks...")
        await self.cleanup_logs()
        await self.cleanup_expired_bans()
        await self.cleanup_expired_mutes()
        await self.cleanup_stale_cache()
        logger.info("Cleanup tasks finished")

    async def cleanup_logs(self) -> int:
        """Delete log files older than configured days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.cleanup_log_days)
        removed = 0
        log_dir = settings.log_dir
        if not log_dir.exists():
            return 0
        for path in log_dir.glob("*.log.*"):
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                try:
                    path.unlink()
                    removed += 1
                except OSError as exc:
                    logger.warning("Could not delete log %s: %s", path, exc)
        logger.info("Log cleanup: removed %d old log files", removed)
        return removed

    async def cleanup_expired_bans(self) -> int:
        """Unban users whose temp ban has expired."""
        async with AsyncSessionFactory() as session:
            now = datetime.now(timezone.utc)
            result = await session.execute(
                update(User)
                .where(
                    User.status == UserStatus.TEMP_BANNED,
                    User.ban_until != None,
                    User.ban_until <= now,
                )
                .values(status=UserStatus.ACTIVE, ban_until=None, ban_reason=None)
            )
            await session.commit()
            count = result.rowcount
        logger.info("Cleanup: lifted %d expired temp bans", count)
        return count

    async def cleanup_expired_mutes(self) -> int:
        """Unmute users whose mute has expired."""
        async with AsyncSessionFactory() as session:
            now = datetime.now(timezone.utc)
            result = await session.execute(
                update(User)
                .where(
                    User.status == UserStatus.MUTED,
                    User.muted_until != None,
                    User.muted_until <= now,
                )
                .values(status=UserStatus.ACTIVE, muted_until=None)
            )
            await session.commit()
            count = result.rowcount
        logger.info("Cleanup: lifted %d expired mutes", count)
        return count

    async def cleanup_stale_cache(self) -> None:
        """Flush expired search cache."""
        await CacheService.delete_pattern("search:*")
        logger.info("Cleanup: flushed stale search cache")

    async def run_scheduler(self) -> None:
        """Background task: runs every 6 hours."""
        logger.info("Cleanup scheduler started")
        while True:
            try:
                await self.run_all()
            except Exception as exc:
                logger.error("Cleanup scheduler error: %s", exc)
            await asyncio.sleep(6 * 3600)
