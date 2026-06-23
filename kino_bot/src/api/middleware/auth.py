"""
API authentication middleware — API Key + JWT Bearer (#20).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy import select, update

from src.core.config import settings
from src.core.security import decode_token, verify_api_key
from src.db.base import AsyncSessionFactory
from src.db.models.api_key import ApiKey

_api_key_header = APIKeyHeader(name=settings.api_key_header, auto_error=False)
_bearer = HTTPBearer(auto_error=False)


async def get_api_key(api_key: Optional[str] = Security(_api_key_header)) -> ApiKey:
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")

    async with AsyncSessionFactory() as session:
        result = await session.execute(select(ApiKey).where(ApiKey.is_active == True))
        keys = result.scalars().all()

    matched = None
    for k in keys:
        if verify_api_key(api_key, k.key_hash):
            matched = k
            break

    if not matched:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    if matched.expires_at and matched.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key expired")

    # Update last used
    async with AsyncSessionFactory() as session:
        await session.execute(
            update(ApiKey)
            .where(ApiKey.id == matched.id)
            .values(last_used=datetime.now(timezone.utc))
        )
        await session.commit()

    return matched


async def get_jwt_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload


# Combined: accept either API key OR JWT
async def get_auth(
    api_key: Optional[str] = Security(_api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
) -> dict:
    if api_key:
        k = await get_api_key(api_key)
        return {"type": "api_key", "id": k.id, "name": k.name}
    if credentials:
        return await get_jwt_user(credentials)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
