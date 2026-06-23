"""
Broadcast REST API endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.middleware.auth import get_auth
from src.db.base import AsyncSessionFactory
from src.db.repositories.broadcast_repo import BroadcastRepository

router = APIRouter(prefix="/broadcasts", tags=["Broadcasts"])


class BroadcastSchema(BaseModel):
    id: int
    title: str
    text: str
    status: str
    scheduled_at: Optional[datetime]
    total_recipients: int
    sent_count: int
    failed_count: int

    model_config = {"from_attributes": True}


class BroadcastCreateSchema(BaseModel):
    title: str
    text: str
    scheduled_at: Optional[datetime] = None
    target_language: Optional[str] = None


@router.get("/", response_model=List[BroadcastSchema])
async def list_broadcasts(auth=Depends(get_auth)):
    async with AsyncSessionFactory() as session:
        broadcasts = await BroadcastRepository(session).list_all()
    return [BroadcastSchema.model_validate(b) for b in broadcasts]


@router.post("/", response_model=BroadcastSchema, status_code=201)
async def create_broadcast(payload: BroadcastCreateSchema, auth=Depends(get_auth)):
    async with AsyncSessionFactory() as session:
        bc = await BroadcastRepository(session).create(
            title=payload.title,
            text=payload.text,
            created_by=0,
            scheduled_at=payload.scheduled_at,
            target_language=payload.target_language,
        )
        await session.commit()
    return BroadcastSchema.model_validate(bc)


@router.delete("/{bc_id}", status_code=204)
async def cancel_broadcast(bc_id: int, auth=Depends(get_auth)):
    async with AsyncSessionFactory() as session:
        success = await BroadcastRepository(session).cancel(bc_id)
        await session.commit()
    if not success:
        raise HTTPException(status_code=404, detail="Broadcast not found or cannot be cancelled")
