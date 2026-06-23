"""
Enterprise configuration management using Pydantic Settings.
All settings are read from environment variables or .env file.
"""
from __future__ import annotations

import secrets
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import AnyUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Telegram ──────────────────────────────────────────────────────────
    bot_token: str = Field(..., description="Telegram Bot Token from @BotFather")
    bot_name: str = Field(default="🎬 Kino Bot Enterprise")
    bot_username: str = Field(default="kino_enterprise_bot")

    # ── Super Admin ───────────────────────────────────────────────────────
    super_admin_id: int = Field(..., description="Telegram user ID of super admin")
    admin_ids: List[int] = Field(default_factory=list)

    # ── Database ──────────────────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://kino:kinopass@localhost:5432/kinodb"
    )
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)
    db_pool_timeout: int = Field(default=30)
    db_echo: bool = Field(default=False)

    # ── Redis ──────────────────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_password: Optional[str] = Field(default=None)
    cache_ttl_search: int = Field(default=300)        # 5 min
    cache_ttl_movie: int = Field(default=3600)        # 1 hour
    cache_ttl_stats: int = Field(default=600)         # 10 min
    cache_ttl_top: int = Field(default=3600)          # 1 hour

    # ── JWT / API Security ─────────────────────────────────────────────────
    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_hex(32))
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_expire_minutes: int = Field(default=60)
    jwt_refresh_expire_days: int = Field(default=30)

    # ── API ────────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")
    api_rate_limit_per_minute: int = Field(default=60)
    api_key_header: str = Field(default="X-API-Key")
    cors_origins: List[str] = Field(default=["*"])

    # ── Dashboard ──────────────────────────────────────────────────────────
    dashboard_host: str = Field(default="0.0.0.0")
    dashboard_port: int = Field(default=8080)
    dashboard_secret_key: str = Field(default_factory=lambda: secrets.token_hex(32))

    # ── Pagination ─────────────────────────────────────────────────────────
    movies_per_page: int = Field(default=10)
    users_per_page: int = Field(default=20)
    search_max_results: int = Field(default=50)

    # ── Watch History ──────────────────────────────────────────────────────
    watch_history_limit: int = Field(default=1000)

    # ── Broadcast ──────────────────────────────────────────────────────────
    broadcast_batch_size: int = Field(default=30)
    broadcast_delay_ms: int = Field(default=50)

    # ── Cleanup ────────────────────────────────────────────────────────────
    cleanup_log_days: int = Field(default=30)
    cleanup_session_days: int = Field(default=7)
    cleanup_backup_days: int = Field(default=90)

    # ── Logging ────────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")
    log_dir: Path = Field(default=BASE_DIR / "logs")
    log_max_bytes: int = Field(default=10 * 1024 * 1024)  # 10 MB
    log_backup_count: int = Field(default=10)

    # ── Feature Flags ──────────────────────────────────────────────────────
    enable_channel_guard: bool = Field(default=False)
    required_channel: Optional[str] = Field(default=None)
    enable_2fa: bool = Field(default=True)
    enable_notifications: bool = Field(default=True)

    # ── Timezone ───────────────────────────────────────────────────────────
    timezone: str = Field(default="Asia/Tashkent")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v or []

    @property
    def all_admin_ids(self) -> List[int]:
        ids = set(self.admin_ids)
        ids.add(self.super_admin_id)
        return list(ids)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
