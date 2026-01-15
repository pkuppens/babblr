import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)


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

    Also runs migrations for existing databases to add missing columns.
    """
    # Import models to ensure they're registered with Base.metadata
    # This import is intentionally here to avoid circular imports at module level
    from app.models import models  # noqa: F401

    logger.info("Initializing database tables...")
    try:
        async with engine.begin() as conn:
            # create_all is idempotent - only creates tables that don't exist
            await conn.run_sync(Base.metadata.create_all)

        # Run migrations for existing databases
        await _migrate_add_topic_id()
        await _migrate_add_mastery_score()

        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def _migrate_add_topic_id():
    """Add topic_id column to conversations table if it doesn't exist."""
    import sqlite3
    from pathlib import Path

    # Get database path from settings
    db_url = settings.babblr_conversation_database_url

    # Extract file path from SQLite URL
    if db_url.startswith("sqlite+aiosqlite:///"):
        db_path = db_url.replace("sqlite+aiosqlite:///", "")
    elif db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        # Not SQLite, skip migration
        return

    db_path = Path(db_path)

    if not db_path.exists():
        # Database will be created with correct schema
        return

    # Use synchronous sqlite3 for migration (simpler for schema changes)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check if topic_id column already exists
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [row[1] for row in cursor.fetchall()]

        if "topic_id" in columns:
            logger.debug("Column topic_id already exists. No migration needed.")
            return

        logger.info("Adding topic_id column to conversations table...")

        # Add topic_id column (nullable, as it's optional)
        cursor.execute("ALTER TABLE conversations ADD COLUMN topic_id VARCHAR(100)")

        conn.commit()
        logger.info("Successfully added topic_id column to conversations table.")

    except sqlite3.Error as e:
        logger.error(f"Error during migration: {e}")
        conn.rollback()
        # Don't raise - allow app to continue even if migration fails
    finally:
        conn.close()


async def _migrate_add_mastery_score():
    """Add mastery_score column to lesson_progress table if it doesn't exist."""
    import sqlite3
    from pathlib import Path

    # Get database path from settings
    db_url = settings.babblr_conversation_database_url

    # Extract file path from SQLite URL
    if db_url.startswith("sqlite+aiosqlite:///"):
        db_path = db_url.replace("sqlite+aiosqlite:///", "")
    elif db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        # Not SQLite, skip migration
        return

    db_path = Path(db_path)

    if not db_path.exists():
        # Database will be created with correct schema
        return

    # Use synchronous sqlite3 for migration (simpler for schema changes)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check if mastery_score column already exists
        cursor.execute("PRAGMA table_info(lesson_progress)")
        columns = [row[1] for row in cursor.fetchall()]

        if "mastery_score" in columns:
            logger.debug("Column mastery_score already exists. No migration needed.")
            return

        logger.info("Adding mastery_score column to lesson_progress table...")

        # Add mastery_score column (nullable, as it's optional)
        cursor.execute("ALTER TABLE lesson_progress ADD COLUMN mastery_score FLOAT")

        conn.commit()
        logger.info("Successfully added mastery_score column to lesson_progress table.")

    except sqlite3.Error as e:
        logger.error(f"Error during migration: {e}")
        conn.rollback()
        # Don't raise - allow app to continue even if migration fails
    finally:
        conn.close()
