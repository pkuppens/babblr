import logging
import sqlite3

# Configure logging for standalone script output
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

conn = sqlite3.connect("babblr.db")
cursor = conn.cursor()

# Check conversations table
cursor.execute("SELECT id, created_at, updated_at FROM conversations LIMIT 5")
logger.info("Conversations:")
logger.info("ID | created_at | updated_at")
for row in cursor.fetchall():
    logger.info(f"{row[0]} | {row[1]} | {row[2]}")

# Count total conversations
cursor.execute("SELECT COUNT(*) FROM conversations")
logger.info(f"\nTotal conversations: {cursor.fetchone()[0]}")

conn.close()
