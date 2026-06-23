"""
Users REST API endpoints.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.middleware.auth import get_auth
from src.db.base import AsyncSessionFactory
from src.db.repositories.user_repo import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])


class UserSchema(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    full_name: str
    language: str
    status: str
    total_searches: int
    total_views: int
    warn_count: int

    model_config = {"from_attributes": True}


class PaginatedUsers(BaseModel):
    items: List[UserSchema]
    total: int
    page: int


@router.get("/", response_model=PaginatedUsers)
async def list_users(
    page: int = Query(0, ge=0),
    per_page: int = Query(20, ge=1, le=100),
    auth=Depends(get_auth),
):
    async with AsyncSessionFactory() as session:
        users, total = await UserRepository(session).get_page(page=page, per_page=per_page)
    return PaginatedUsers(
        items=[UserSchema.model_validate(u) for u in users],
        total=total,
        page=page,
    )


@router.get("/{telegram_id}", response_model=UserSchema)
async def get_user(telegram_id: int, auth=Depends(get_auth)):
    async with AsyncSessionFactory() as session:
        user = await UserRepository(session).get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserSchema.model_validate(user)


@router.post("/{telegram_id}/block")
async def block_user(telegram_id: int, reason: str = "Admin", auth=Depends(get_auth)):
    async with AsyncSessionFactory() as session:
        success = await UserRepository(session).block_user(telegram_id, reason)
        await session.commit()
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "blocked"}


@router.post("/{telegram_id}/unblock")
async def unblock_user(telegram_id: int, auth=Depends(get_auth)):
    async with AsyncSessionFactory() as session:
        success = await UserRepository(session).unblock_user(telegram_id)
        await session.commit()
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "unblocked"}
