"""
Security utilities: JWT, password hashing, 2FA (TOTP), API key generation.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import pyotp
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password ──────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as exc:
        logger.warning("JWT decode failed: %s", exc)
        return None


# ── 2FA (TOTP) ────────────────────────────────────────────────────────────────

def generate_2fa_secret() -> str:
    return pyotp.random_base32()


def get_2fa_uri(secret: str, username: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=settings.bot_name)


def verify_2fa_code(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


# ── API Key ───────────────────────────────────────────────────────────────────

def generate_api_key() -> str:
    return f"kb_{secrets.token_urlsafe(32)}"


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_api_key(plain), hashed)


# ── Input Sanitisation ────────────────────────────────────────────────────────

def sanitise_input(value: str, max_length: int = 500) -> str:
    """Strip dangerous characters and enforce max length."""
    dangerous = ["<", ">", "{", "}", "\\", ";", "--", "/*", "*/"]
    result = value.strip()[:max_length]
    for char in dangerous:
        result = result.replace(char, "")
    return result
