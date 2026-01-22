import sqlite3

conn = sqlite3.connect("babblr.db")
cursor = conn.cursor()

# Check conversations table
cursor.execute("SELECT id, created_at, updated_at FROM conversations LIMIT 5")
print("Conversations:")
print("ID | created_at | updated_at")
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]}")

# Count total conversations
cursor.execute("SELECT COUNT(*) FROM conversations")
print(f"\nTotal conversations: {cursor.fetchone()[0]}")

conn.close()
