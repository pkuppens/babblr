import logging
from datetime import datetime, timezone

from sqlalchemy import DateTime, TypeDecorator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)


class TZDateTime(TypeDecorator):
    """Timezone-aware DateTime type for SQLite compatibility.

    SQLite doesn't natively support timezone-aware datetimes. This TypeDecorator
    ensures that datetimes are always timezone-aware UTC when loaded from the database,
    converting naive datetimes to UTC if necessary.

    Per ADR-0001, all timestamps should be stored and retrieved as timezone-aware UTC.
    """

    impl = DateTime
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Return the underlying DateTime type with timezone support."""
        return dialect.type_descriptor(DateTime(timezone=True))

    def process_result_value(self, value, dialect):
        """Convert retrieved datetime to timezone-aware UTC if needed."""
        if value is None:
            return None
        if isinstance(value, datetime):
            # If datetime is naive, assume it's UTC and make it timezone-aware
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            # If datetime is timezone-aware, ensure it's UTC
            return value.astimezone(timezone.utc)
        return value


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Create async engine
engine = create_async_engine(settings.babblr_conversation_database_url, echo=True, future=True)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


async def get_db():
    """Dependency for getting database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables (idempotent - safe to call multiple times).

    Creates all tables from SQLAlchemy models with the correct schema.
    All datetime columns use timezone-aware UTC defaults as per ADR-0001.
    """
    # Import models to ensure they're registered with Base.metadata
    # This import is intentionally here to avoid circular imports at module level
    from app.models import models  # noqa: F401

    logger.info("Initializing database tables...")
    try:
        async with engine.begin() as conn:
            # create_all is idempotent - only creates tables that don't exist
            # All models already have correct timezone-aware UTC defaults
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables initialized successfully")
    except Exception as e:
        error_msg = (
            f"Failed to initialize database: {e}\n"
            "This usually means:\n"
            "1. The database file is corrupted or locked\n"
            "2. There are permission issues with the database file\n"
            "Try: Delete the database file and restart (it will be recreated)"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
