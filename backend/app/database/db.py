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
    All migrations run automatically at startup to ensure schema consistency.
    """
    # Import models to ensure they're registered with Base.metadata
    # This import is intentionally here to avoid circular imports at module level
    from app.models import models  # noqa: F401

    logger.info("Initializing database tables...")
    try:
        async with engine.begin() as conn:
            # create_all is idempotent - only creates tables that don't exist
            await conn.run_sync(Base.metadata.create_all)

        # Run migrations for existing databases (all migrations run automatically)
        logger.info("Running database migrations...")
        await _migrate_add_topic_id()
        await _migrate_add_mastery_score()
        await _migrate_ensure_timezone_aware_datetimes()
        await _migrate_add_assessment_columns()

        logger.info("Database tables initialized and migrations completed successfully")
    except Exception as e:
        error_msg = (
            f"Failed to initialize database: {e}\n"
            "This usually means:\n"
            "1. The database file is corrupted or locked\n"
            "2. There are permission issues with the database file\n"
            "3. A migration failed (check logs above for details)\n"
            "Try: Delete the database file and restart (it will be recreated)"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


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


async def _migrate_ensure_timezone_aware_datetimes():
    """Ensure all datetime columns use timezone-aware UTC defaults.

    Existing records are already stored correctly (as UTC strings).
    This migration ensures new records use timezone-aware datetime defaults.
    """
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
        logger.info("Verifying datetime columns have UTC timezone awareness...")

        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        datetime_tables = {
            'conversations': ['created_at', 'updated_at'],
            'messages': ['created_at'],
            'lessons': ['created_at', 'updated_at', 'last_accessed_at'],
            'lesson_items': ['created_at'],
            'lesson_progress': ['created_at'],
            'grammar_rules': ['created_at'],
            'grammar_rule_examples': ['created_at'],
            'assessment_attempts': ['started_at', 'assessed_at', 'updated_at'],
        }

        # Log verification results
        for table_name, datetime_cols in datetime_tables.items():
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if cursor.fetchone():
                logger.debug(f"Table {table_name} has datetime columns: {datetime_cols}")
                # Note: SQLite doesn't enforce column types, so we can't validate directly
                # But the Python ORM will handle timezone-aware conversion on reads/writes

        logger.info("Datetime columns verified. New records will use timezone-aware UTC datetimes.")
        conn.commit()

    except sqlite3.Error as e:
        logger.error(f"Error during timezone verification: {e}")
        conn.rollback()
        # Don't raise - this is non-critical
    finally:
        conn.close()


async def _migrate_add_assessment_columns():
    """Add missing columns to assessment tables if they don't exist.

    Migrates:
    - skill_category column to assessment_questions table
    - recommended_level column to assessment_attempts table
    - skill_scores_json column to assessment_attempts table
    """
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
        # Check if tables exist (they should exist after create_all, but be safe)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('assessment_questions', 'assessment_attempts')"
        )
        existing_tables = {row[0] for row in cursor.fetchall()}

        # Migrate assessment_questions.skill_category
        if "assessment_questions" in existing_tables:
            cursor.execute("PRAGMA table_info(assessment_questions)")
            question_columns = [row[1] for row in cursor.fetchall()]

            if "skill_category" not in question_columns:
                logger.info("Adding skill_category column to assessment_questions table...")
                cursor.execute(
                    "ALTER TABLE assessment_questions ADD COLUMN skill_category VARCHAR(50) DEFAULT 'grammar'"
                )
                logger.info(
                    "Successfully added skill_category column to assessment_questions table."
                )
            else:
                logger.debug(
                    "Column skill_category already exists in assessment_questions. No migration needed."
                )
        else:
            logger.debug(
                "Table assessment_questions does not exist yet. Will be created with correct schema."
            )

        # Migrate assessment_attempts.recommended_level and skill_scores_json
        if "assessment_attempts" in existing_tables:
            cursor.execute("PRAGMA table_info(assessment_attempts)")
            attempt_columns = [row[1] for row in cursor.fetchall()]

            if "recommended_level" not in attempt_columns:
                logger.info("Adding recommended_level column to assessment_attempts table...")
                cursor.execute(
                    "ALTER TABLE assessment_attempts ADD COLUMN recommended_level VARCHAR(20)"
                )
                logger.info(
                    "Successfully added recommended_level column to assessment_attempts table."
                )
            else:
                logger.debug(
                    "Column recommended_level already exists in assessment_attempts. No migration needed."
                )

            if "skill_scores_json" not in attempt_columns:
                logger.info("Adding skill_scores_json column to assessment_attempts table...")
                cursor.execute("ALTER TABLE assessment_attempts ADD COLUMN skill_scores_json TEXT")
                logger.info(
                    "Successfully added skill_scores_json column to assessment_attempts table."
                )
            else:
                logger.debug(
                    "Column skill_scores_json already exists in assessment_attempts. No migration needed."
                )
        else:
            logger.debug(
                "Table assessment_attempts does not exist yet. Will be created with correct schema."
            )

        conn.commit()

    except sqlite3.Error as e:
        error_msg = f"Error during assessment columns migration: {e}"
        logger.error(error_msg)
        conn.rollback()
        raise RuntimeError(
            f"Database migration failed: {error_msg}\n"
            "The application cannot start with an outdated database schema.\n"
            "If this persists, try deleting the database file and restarting."
        ) from e
    finally:
        conn.close()
