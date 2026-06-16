from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import logging

from .config import settings
from ..models.base import Base

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    str(settings.database_url),
    echo=settings.environment == "development",
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    poolclass=NullPool if settings.environment == "testing" else None,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session in FastAPI."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def drop_db() -> None:
    """Drop all database tables (use with caution)."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


async def close_db() -> None:
    """Close database connection."""
    await engine.dispose()
