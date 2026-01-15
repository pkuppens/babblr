"""Migration script to add mastery_score column to lesson_progress table.

This script adds the mastery_score column to the existing lesson_progress table.
Run this if you have an existing database that was created before mastery_score was added.

Usage:
    cd backend
    python -m app.scripts.migrate_add_mastery_score
"""

import logging
import sqlite3
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_add_mastery_score():
    """Add mastery_score column to lesson_progress table if it doesn't exist."""
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
        # Check if mastery_score column already exists
        cursor.execute("PRAGMA table_info(lesson_progress)")
        columns = [row[1] for row in cursor.fetchall()]

        if "mastery_score" in columns:
            logger.info("Column mastery_score already exists. No migration needed.")
            return

        logger.info("Adding mastery_score column to lesson_progress table...")

        # Add mastery_score column (nullable, as it's optional)
        cursor.execute("ALTER TABLE lesson_progress ADD COLUMN mastery_score FLOAT")

        conn.commit()
        logger.info("Successfully added mastery_score column to lesson_progress table.")

    except sqlite3.Error as e:
        logger.error(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    """Run the migration."""
    migrate_add_mastery_score()


if __name__ == "__main__":
    main()
