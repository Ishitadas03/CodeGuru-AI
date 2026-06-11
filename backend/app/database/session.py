# backend/app/database/session.py
"""Async SQLAlchemy engine and session configuration.

Supports both PostgreSQL (production) and SQLite (development) with proper
connection pool settings. The engine is configured with pool pre-ping for
connection health validation.
"""
from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

logger = logging.getLogger("codeguru.database")

# Determine engine kwargs based on the database driver.
# SQLite (aiosqlite) does not support connection pooling parameters.
_is_sqlite = settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite")

engine_kwargs: dict = {
    "echo": settings.DB_ECHO,
}

if not _is_sqlite:
    engine_kwargs.update(
        {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_pre_ping": settings.DB_POOL_PRE_PING,
            "pool_recycle": 3600,  # Recycle connections after 1 hour
        }
    )
else:
    logger.info("Using SQLite backend — connection pooling parameters are skipped.")

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    **engine_kwargs,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    The session is automatically closed when the request completes,
    ensuring no leaked connections.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
