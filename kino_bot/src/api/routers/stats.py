"""
Statistics REST API endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from src.api.middleware.auth import get_auth
from src.services.analytics import AnalyticsService

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/overview")
async def get_overview(auth=Depends(get_auth)):
    service = AnalyticsService()
    return await service.get_overview()


@router.get("/period")
async def get_period(
    period: str = Query("weekly", regex="^(weekly|monthly|yearly)$"),
    auth=Depends(get_auth),
):
    service = AnalyticsService()
    return await service.get_period_stats(period)
