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
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC - Generated parquet files in `databricks/data/` (run `python generate_synthetic_data.py` locally)
# MAGIC - Uploaded files to **Unity Catalog Volumes** (required for Spark access in Free Edition):
# MAGIC   - Create catalog (typically `workspace` in Free Edition) → Schema `babblr` → Volume `bronze`
# MAGIC   - Upload all 7 parquet files locally to `/Volumes/<catalog>/babblr/bronze/`
# MAGIC   - **Note**: This tutorial uses local file uploads (not external AWS/S3 volumes)
# MAGIC
# MAGIC > **Important**: Workspace folders cannot be accessed directly by Spark for data files. You must use Unity Catalog Volumes for medallion architecture. See the validation guide (section 2.2) for step-by-step instructions.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup: Define paths and database

# COMMAND ----------

# Configuration
# IMPORTANT: Unity Catalog Volumes are required for Spark to access data files.
# Workspace folders cannot be accessed directly by Spark for data files.
# For Free Edition: Use local file uploads to Unity Catalog Volumes (not external AWS/S3 volumes).

# Common catalog names to try (Free Edition typically uses 'workspace')
# Replace with your catalog name if different
COMMON_CATALOGS = ["workspace", "main", "hive_metastore"]

# Build list of possible Volume paths
POSSIBLE_PATHS = []
for catalog in COMMON_CATALOGS:
    POSSIBLE_PATHS.append(f"/Volumes/{catalog}/babblr/bronze")

# Also try DBFS FileStore (may be restricted in Free Edition)
POSSIBLE_PATHS.append("/FileStore/babblr/bronze")

DATABASE_NAME = "babblr_bronze"

# Detect which path is available
BRONZE_PATH = None
for path in POSSIBLE_PATHS:
    try:
        files = dbutils.fs.ls(path)
        if files:  # Check that directory exists and has files
            BRONZE_PATH = path
            print(f"[OK] Found accessible path: {BRONZE_PATH}")
            print(f"     Found {len(files)} file(s) in directory")
            break
    except Exception as e:
        continue

if BRONZE_PATH is None:
    print("[ERROR] No accessible storage path found!")
    print("\n[SOLUTION] You must use Unity Catalog Volumes (local file uploads in Free Edition):")
    print("   1. Go to Catalog in sidebar")
    print("   2. Create or select a catalog (typically 'workspace' in Free Edition)")
    print("   3. Create schema 'babblr'")
    print("   4. Create volume 'bronze'")
    print("   5. Upload all 7 parquet files locally to the volume (not external AWS/S3)")
    print("   6. Files will be at: /Volumes/<catalog>/babblr/bronze/")
    print("\n   Workspace folders do NOT work for Spark data access.")
    print("   See VALIDATION.md section 2.2 for detailed steps.")
    raise FileNotFoundError("No accessible data path found. Please use Unity Catalog Volumes.")

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

%%sql
-- Show all tables in the bronze database
SHOW TABLES

# COMMAND ----------

%%sql
-- Quick preview of conversations table
SELECT * FROM conversations LIMIT 5

# COMMAND ----------

%%sql
-- Check data distribution by language
SELECT
    language,
    COUNT(*) as conversation_count,
    COUNT(DISTINCT user_id) as unique_users
FROM conversations
GROUP BY language
ORDER BY conversation_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Delta Lake Feature: Table History
# MAGIC
# MAGIC Delta Lake automatically tracks all changes to tables.

# COMMAND ----------

%%sql
-- View table history (time travel metadata)
DESCRIBE HISTORY conversations

# COMMAND ----------

# MAGIC %md
# MAGIC ## Delta Lake Feature: Schema Information

# COMMAND ----------

%%sql
-- View schema of a table
DESCRIBE TABLE EXTENDED conversations

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
