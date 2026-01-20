# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer - Raw Data Ingestion
# MAGIC
# MAGIC This notebook demonstrates loading raw Parquet files into Delta Lake tables.
# MAGIC
# MAGIC **Key Concepts:**
# MAGIC - Delta Lake table creation
# MAGIC - Schema inference from Parquet
# MAGIC - DBFS file access

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup: Define paths and database

# COMMAND ----------

# Configuration
# For Free Edition: Use Volumes or upload files directly to workspace
# Try these paths in order (first available will be used):
POSSIBLE_PATHS = [
    "/Volumes/babblr/bronze",  # Volumes (Free Edition compatible)
    "/FileStore/babblr/bronze",  # DBFS FileStore (may be restricted in Free Edition)
    "/Workspace/babblr/bronze",  # Workspace files (alternative)
]

DATABASE_NAME = "babblr_bronze"

# Detect which path is available
BRONZE_PATH = None
for path in POSSIBLE_PATHS:
    try:
        dbutils.fs.ls(path)
        BRONZE_PATH = path
        print(f"✓ Found accessible path: {BRONZE_PATH}")
        break
    except Exception:
        continue

if BRONZE_PATH is None:
    print("⚠ No accessible storage path found. For Free Edition:")
    print("   1. Upload files using 'Upload Data' in the workspace")
    print("   2. Or use Volumes: Create a Volume at /Volumes/babblr/bronze")
    print("   3. Or upload files directly in this notebook using:")
    print("      dbutils.fs.put('/tmp/your_file.parquet', file_content)")
    print("\n   Then update BRONZE_PATH above to match your upload location.")
    BRONZE_PATH = "/tmp/babblr/bronze"  # Fallback to temp location
    print(f"\n   Using fallback path: {BRONZE_PATH}")

# Create database if not exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
spark.sql(f"USE {DATABASE_NAME}")

print(f"Using database: {DATABASE_NAME}")
print(f"Using bronze path: {BRONZE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## List available data files

# COMMAND ----------

# Check what files are available
try:
    files = dbutils.fs.ls(BRONZE_PATH)
    print("Available files in bronze layer:")
    for f in files:
        print(f"  - {f.name} ({f.size / 1024:.1f} KB)")
except Exception as e:
    print(f"Error: {e}")
    print(f"\nPlease upload Parquet files to {BRONZE_PATH}")
    print("Run generate_synthetic_data.py locally first, then upload the data/ folder")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load tables into Delta format
# MAGIC
# MAGIC Delta Lake provides:
# MAGIC - ACID transactions
# MAGIC - Time travel (versioning)
# MAGIC - Schema enforcement

# COMMAND ----------

def load_to_delta(table_name: str):
    """Load a Parquet file into a Delta table."""
    parquet_path = f"{BRONZE_PATH}/{table_name}.parquet"

    try:
        # Read Parquet with schema inference
        df = spark.read.parquet(parquet_path)

        # Write as Delta table (overwrite for demo purposes)
        df.write.format("delta").mode("overwrite").saveAsTable(table_name)

        row_count = spark.table(table_name).count()
        print(f"[OK] {table_name}: {row_count} rows loaded")
        return row_count
    except Exception as e:
        print(f"[SKIP] {table_name}: {e}")
        return 0

# COMMAND ----------

# Load all tables
tables = [
    "conversations",
    "messages",
    "lessons",
    "lesson_progress",
    "assessments",
    "assessment_attempts",
    "user_levels"
]

total_rows = 0
for table in tables:
    total_rows += load_to_delta(table)

print(f"\nTotal: {total_rows} rows loaded into Delta tables")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Delta tables

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Show all tables in the bronze database
# MAGIC SHOW TABLES

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Quick preview of conversations table
# MAGIC SELECT * FROM conversations LIMIT 5

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check data distribution by language
# MAGIC SELECT
# MAGIC     language,
# MAGIC     COUNT(*) as conversation_count,
# MAGIC     COUNT(DISTINCT user_id) as unique_users
# MAGIC FROM conversations
# MAGIC GROUP BY language
# MAGIC ORDER BY conversation_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Delta Lake Feature: Table History
# MAGIC
# MAGIC Delta Lake automatically tracks all changes to tables.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- View table history (time travel metadata)
# MAGIC DESCRIBE HISTORY conversations

# COMMAND ----------

# MAGIC %md
# MAGIC ## Delta Lake Feature: Schema Information

# COMMAND ----------

# MAGIC %sql
# MAGIC -- View schema of a table
# MAGIC DESCRIBE TABLE EXTENDED conversations

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC In this notebook we:
# MAGIC 1. Created a Bronze database for raw data
# MAGIC 2. Loaded Parquet files into Delta Lake tables
# MAGIC 3. Verified data with basic queries
# MAGIC 4. Demonstrated Delta Lake features (history, schema)
# MAGIC
# MAGIC **Next:** Run `02_silver_layer` to clean and transform the data.
