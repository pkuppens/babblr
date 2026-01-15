"""Migration script to add topic_id column to conversations table.

This script adds the topic_id column to the existing conversations table.
Run this if you have an existing database that was created before topic_id was added.
"""

import asyncio
import logging
import sqlite3
from pathlib import Path

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_add_topic_id():
    """Add topic_id column to conversations table if it doesn't exist."""
    # Get database path from settings
    db_url = settings.babblr_conversation_database_url

    # Extract file path from SQLite URL (sqlite+aiosqlite:///path/to/db.db)
    if db_url.startswith("sqlite+aiosqlite:///"):
        db_path = db_url.replace("sqlite+aiosqlite:///", "")
    elif db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        logger.error(f"Unsupported database URL format: {db_url}")
        return

    db_path = Path(db_path)

    if not db_path.exists():
        logger.info(
            f"Database {db_path} does not exist. It will be created with the correct schema on next startup."
        )
        return

    logger.info(f"Checking database schema at {db_path}")

    # Use synchronous sqlite3 for migration (simpler for schema changes)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check if topic_id column already exists
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [row[1] for row in cursor.fetchall()]

        if "topic_id" in columns:
            logger.info("Column topic_id already exists. No migration needed.")
            return

        logger.info("Adding topic_id column to conversations table...")

        # Add topic_id column (nullable, as it's optional)
        cursor.execute("ALTER TABLE conversations ADD COLUMN topic_id VARCHAR(100)")

        conn.commit()
        logger.info("Successfully added topic_id column to conversations table.")

    except sqlite3.Error as e:
        logger.error(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    asyncio.run(migrate_add_topic_id())
