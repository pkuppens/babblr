"""Migration script to add new fields to lessons table.

This script adds the following columns to the existing lessons table:
- oneliner: Brief one-sentence description
- tutor_prompt: LLM prompt for content generation
- subject: Subject/topic identifier
- topic_id: Link to vocabulary topic
- updated_at: Track when lesson was last modified
- last_accessed_at: Track when lesson was last accessed

Run this if you have an existing database that was created before these fields were added.

Usage:
    cd backend
    python -m app.scripts.migrate_add_lesson_fields
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


def migrate_add_lesson_fields():
    """Add new fields to lessons table if they don't exist."""
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
        # Check existing columns
        cursor.execute("PRAGMA table_info(lessons)")
        columns = {row[1]: row for row in cursor.fetchall()}

        fields_to_add = [
            ("oneliner", "VARCHAR(500)"),
            ("tutor_prompt", "TEXT"),
            ("subject", "VARCHAR(100)"),
            ("topic_id", "VARCHAR(100)"),
            ("updated_at", "DATETIME"),
            ("last_accessed_at", "DATETIME"),
        ]

        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                logger.info(f"Adding {field_name} column to lessons table...")
                cursor.execute(f"ALTER TABLE lessons ADD COLUMN {field_name} {field_type}")
                logger.info(f"Successfully added {field_name} column.")
            else:
                logger.info(f"Column {field_name} already exists. Skipping.")

        # Set default updated_at to created_at for existing rows
        if "updated_at" not in columns:
            cursor.execute("UPDATE lessons SET updated_at = created_at WHERE updated_at IS NULL")

        conn.commit()
        logger.info("Migration completed successfully.")

    except sqlite3.Error as e:
        logger.error(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    """Run the migration."""
    migrate_add_lesson_fields()


if __name__ == "__main__":
    main()
