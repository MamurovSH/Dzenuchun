"""
Structured logging configuration with rotation and JSON support.
"""
from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

from src.core.config import settings


def setup_logging() -> None:
    """Configure application-wide logging."""
    log_dir: Path = settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=date_fmt)

    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    # Rotating file handler — all logs
    file_all = logging.handlers.RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_all.setFormatter(formatter)
    root.addHandler(file_all)

    # Rotating file handler — errors only
    file_err = logging.handlers.RotatingFileHandler(
        filename=log_dir / "errors.log",
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_err.setLevel(logging.ERROR)
    file_err.setFormatter(formatter)
    root.addHandler(file_err)

    # Silence noisy third-party loggers
    for noisy in ("aiohttp", "asyncio", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info("Logging initialised — level=%s", settings.log_level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
