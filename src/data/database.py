"""
Database configuration and connection management.

Uses SQLAlchemy 2.0 async with asyncpg for PostgreSQL.
Recommended: Neon (https://neon.tech) for free PostgreSQL hosting.
"""

import ssl
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.settings import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Get database URL and remove sslmode from query string (asyncpg handles it differently)
db_url = settings.database_url.get_secret_value()
# Remove sslmode parameter as asyncpg uses ssl context instead
if "?" in db_url:
    base_url, params = db_url.split("?", 1)
    filtered_params = "&".join(
        p for p in params.split("&") 
        if not p.startswith("sslmode=") and not p.startswith("channel_binding=")
    )
    db_url = f"{base_url}?{filtered_params}" if filtered_params else base_url

# Create SSL context for Neon
ssl_context = ssl.create_default_context()

# Create async engine with SSL for Neon
engine = create_async_engine(
    db_url,
    echo=settings.is_development,  # Log SQL in development
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,
    max_overflow=10,
    connect_args={"ssl": ssl_context},  # asyncpg SSL configuration
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.
    
    Usage:
        async with get_session() as session:
            result = await session.execute(select(Opportunity))
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined in SQLAlchemy models.
    Run this once on startup or use Alembic for migrations.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


# Alias for backwards compatibility
get_db_session = get_session


# Alias for backward compatibility
get_db_session = get_session
