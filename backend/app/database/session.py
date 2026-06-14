"""Async SQLAlchemy engine and session configuration.

Configured for serverless deployments (Vercel):
- Minimal connection pool (each invocation is stateless)
- Connection recycling to avoid stale connections
- No persistent pool across invocations
"""
from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

logger = logging.getLogger("codeguru.database")

# Determine engine kwargs based on the database driver.
_is_sqlite = settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite")

# Serverless-optimized pool settings:
# - pool_size=1: each function invocation needs at most 1 connection
# - max_overflow=0: don't allow burst connections (serverless = 1 concurrent req per instance)
# - pool_pre_ping: validate connections before use (critical for serverless cold starts)
# - pool_recycle=300: recycle connections every 5 min (Vercel functions live ~5 min)
engine_kwargs: dict = {
    "echo": settings.DB_ECHO,
}

if not _is_sqlite:
    engine_kwargs.update(
        {
            "pool_size": 1,
            "max_overflow": 0,
            "pool_pre_ping": True,
            "pool_recycle": 300,
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
