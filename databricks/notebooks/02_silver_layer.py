# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer - Data Cleaning & Transformations
# MAGIC
# MAGIC This notebook transforms raw Bronze data into cleaned, joined Silver tables.
# MAGIC
# MAGIC **Key Concepts:**
# MAGIC - Spark SQL transformations
# MAGIC - JSON parsing with `from_json`
# MAGIC - Window functions
# MAGIC - Data quality checks
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **Prerequisites:** Run `01_bronze_layer` first to create the bronze tables.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StructType, StructField, StringType, FloatType, IntegerType

# Configuration
BRONZE_DB = "babblr_bronze"
SILVER_DB = "babblr_silver"

# Create silver database
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SILVER_DB}")
print(f"Silver database: {SILVER_DB}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Clean Conversations Table
# MAGIC
# MAGIC - Parse timestamps
# MAGIC - Add derived columns (conversation duration, message count)

# COMMAND ----------

# Read bronze conversations and messages
conversations = spark.table(f"{BRONZE_DB}.conversations")
messages = spark.table(f"{BRONZE_DB}.messages")

# Calculate conversation metrics
conv_metrics = messages.groupBy("conversation_id").agg(
    F.count("*").alias("message_count"),
    F.sum(F.when(F.col("role") == "user", 1).otherwise(0)).alias("user_messages"),
    F.sum(F.when(F.col("corrections").isNotNull(), 1).otherwise(0)).alias("messages_with_errors")
)

# Join and create silver conversations
silver_conversations = (
    conversations
    .join(conv_metrics, conversations.id == conv_metrics.conversation_id, "left")
    .withColumn("created_at", F.to_timestamp("created_at"))
    .withColumn("updated_at", F.to_timestamp("updated_at"))
    .withColumn(
        "duration_minutes",
        (F.unix_timestamp("updated_at") - F.unix_timestamp("created_at")) / 60
    )
    .withColumn(
        "error_rate",
        F.when(F.col("user_messages") > 0,
               F.col("messages_with_errors") / F.col("user_messages")
        ).otherwise(0)
    )
    .select(
        "id", "user_id", "language", "difficulty_level", "topic_id",
        "created_at", "updated_at", "message_count", "user_messages",
        "messages_with_errors", "duration_minutes", "error_rate"
    )
)

# Save to silver
silver_conversations.write.format("delta").mode("overwrite").saveAsTable(f"{SILVER_DB}.conversations")
print(f"Silver conversations: {silver_conversations.count()} rows")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Preview silver conversations
# MAGIC SELECT * FROM babblr_silver.conversations LIMIT 5

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Parse Message Corrections (JSON)
# MAGIC
# MAGIC Demonstrates parsing JSON columns into structured data.

# COMMAND ----------

# Define schema for corrections JSON
corrections_schema = ArrayType(StructType([
    StructField("type", StringType(), True),
    StructField("original", StringType(), True),
    StructField("corrected", StringType(), True),
    StructField("explanation", StringType(), True)
]))

# Parse corrections JSON
silver_messages = (
    messages
    .withColumn("created_at", F.to_timestamp("created_at"))
    .withColumn(
        "corrections_parsed",
        F.when(
            F.col("corrections").isNotNull() & (F.col("corrections") != "null"),
            F.from_json("corrections", corrections_schema)
        ).otherwise(F.lit(None))
    )
    .withColumn(
        "error_count",
        F.when(F.col("corrections_parsed").isNotNull(),
               F.size("corrections_parsed")
        ).otherwise(0)
    )
    .withColumn("content_length", F.length("content"))
)

silver_messages.write.format("delta").mode("overwrite").saveAsTable(f"{SILVER_DB}.messages")
print(f"Silver messages: {silver_messages.count()} rows")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- View messages with parsed corrections
# MAGIC SELECT
# MAGIC     id,
# MAGIC     role,
# MAGIC     content_length,
# MAGIC     error_count,
# MAGIC     corrections_parsed
# MAGIC FROM babblr_silver.messages
# MAGIC WHERE error_count > 0
# MAGIC LIMIT 5

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Enrich Lesson Progress with Lesson Details

# COMMAND ----------

lessons = spark.table(f"{BRONZE_DB}.lessons")
lesson_progress = spark.table(f"{BRONZE_DB}.lesson_progress").withColumnRenamed("id", "progress_id")

# Join progress with lesson details
silver_lesson_progress = (
    lesson_progress
    .join(
        lessons.select("id", "lesson_type", "subject", "title", "difficulty_level"),
        lesson_progress.lesson_id == lessons.id,
        "left"
    )
    .withColumnRenamed("difficulty_level", "lesson_difficulty")
    .withColumn("started_at", F.to_timestamp("started_at"))
    .withColumn("completed_at", F.to_timestamp("completed_at"))
    .withColumn("last_accessed_at", F.to_timestamp("last_accessed_at"))
    .withColumn(
        "time_to_complete_hours",
        F.when(
            F.col("completed_at").isNotNull(),
            (F.unix_timestamp("completed_at") - F.unix_timestamp("started_at")) / 3600
        ).otherwise(None)
    )
    .select(
        "progress_id", "user_id", "lesson_id", "language", "lesson_type", "subject",
        "title", "lesson_difficulty", "status", "completion_percentage", "mastery_score",
        "started_at", "completed_at", "last_accessed_at", "time_to_complete_hours"
    )
)

silver_lesson_progress.write.format("delta").mode("overwrite").saveAsTable(f"{SILVER_DB}.lesson_progress")
print(f"Silver lesson progress: {silver_lesson_progress.count()} rows")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Lesson completion stats by type
# MAGIC SELECT
# MAGIC     lesson_type,
# MAGIC     COUNT(*) as total_attempts,
# MAGIC     SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
# MAGIC     ROUND(AVG(mastery_score), 3) as avg_mastery,
# MAGIC     ROUND(AVG(time_to_complete_hours), 2) as avg_hours_to_complete
# MAGIC FROM babblr_silver.lesson_progress
# MAGIC GROUP BY lesson_type

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Parse Assessment Skill Scores (JSON)

# COMMAND ----------

assessment_attempts = spark.table(f"{BRONZE_DB}.assessment_attempts").withColumnRenamed("id", "attempt_id")
assessments = spark.table(f"{BRONZE_DB}.assessments")

# Define schema for skill scores JSON
skill_schema = ArrayType(StructType([
    StructField("skill", StringType(), True),
    StructField("total", IntegerType(), True),
    StructField("correct", IntegerType(), True),
    StructField("score", FloatType(), True)
]))

# Join and parse skill scores
silver_attempts = (
    assessment_attempts
    .join(
        assessments.select("id", "assessment_type", "title", "difficulty_level"),
        assessment_attempts.assessment_id == assessments.id,
        "left"
    )
    .withColumnRenamed("difficulty_level", "assessment_difficulty")
    .withColumn("started_at", F.to_timestamp("started_at"))
    .withColumn("completed_at", F.to_timestamp("completed_at"))
    .withColumn(
        "skill_scores_parsed",
        F.from_json("skill_scores_json", skill_schema)
    )
    .withColumn(
        "duration_minutes",
        (F.unix_timestamp("completed_at") - F.unix_timestamp("started_at")) / 60
    )
    .select(
        "attempt_id", "user_id", "assessment_id", "language", "assessment_type",
        "title", "assessment_difficulty", "score", "total_questions", "correct_answers",
        "started_at", "completed_at", "duration_minutes", "recommended_level",
        "skill_scores_parsed"
    )
)

silver_attempts.write.format("delta").mode("overwrite").saveAsTable(f"{SILVER_DB}.assessment_attempts")
print(f"Silver assessment attempts: {silver_attempts.count()} rows")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Assessment performance by type
# MAGIC SELECT
# MAGIC     assessment_type,
# MAGIC     COUNT(*) as attempts,
# MAGIC     ROUND(AVG(score), 1) as avg_score,
# MAGIC     ROUND(AVG(duration_minutes), 1) as avg_duration_min
# MAGIC FROM babblr_silver.assessment_attempts
# MAGIC GROUP BY assessment_type
# MAGIC ORDER BY attempts DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Create User Profiles with Window Functions

# COMMAND ----------

user_levels = spark.table(f"{BRONZE_DB}.user_levels")

# Calculate user stats using window functions
from pyspark.sql.window import Window

user_window = Window.partitionBy("user_id").orderBy("started_at")

# Get user activity summary
user_activity = (
    silver_attempts
    .withColumn("attempt_number", F.row_number().over(user_window))
    .withColumn("prev_score", F.lag("score").over(user_window))
    .withColumn("score_improvement", F.col("score") - F.col("prev_score"))
)

# Aggregate to user level
silver_users = (
    user_activity
    .groupBy("user_id", "language")
    .agg(
        F.count("*").alias("total_assessments"),
        F.round(F.avg("score"), 1).alias("avg_score"),
        F.round(F.avg("score_improvement"), 2).alias("avg_improvement"),
        F.max("recommended_level").alias("current_level"),
        F.min("started_at").alias("first_activity"),
        F.max("completed_at").alias("last_activity")
    )
    .join(
        user_levels.select("user_id", "proficiency_score"),
        "user_id",
        "left"
    )
)

silver_users.write.format("delta").mode("overwrite").saveAsTable(f"{SILVER_DB}.user_profiles")
print(f"Silver user profiles: {silver_users.count()} rows")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- User profiles preview
# MAGIC SELECT * FROM babblr_silver.user_profiles
# MAGIC ORDER BY total_assessments DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Summary

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Summary of silver layer tables
# MAGIC SELECT 'conversations' as table_name, COUNT(*) as row_count FROM babblr_silver.conversations
# MAGIC UNION ALL
# MAGIC SELECT 'messages', COUNT(*) FROM babblr_silver.messages
# MAGIC UNION ALL
# MAGIC SELECT 'lesson_progress', COUNT(*) FROM babblr_silver.lesson_progress
# MAGIC UNION ALL
# MAGIC SELECT 'assessment_attempts', COUNT(*) FROM babblr_silver.assessment_attempts
# MAGIC UNION ALL
# MAGIC SELECT 'user_profiles', COUNT(*) FROM babblr_silver.user_profiles

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC In this notebook we:
# MAGIC 1. Cleaned and enriched conversations with metrics
# MAGIC 2. Parsed JSON corrections from messages
# MAGIC 3. Joined lesson progress with lesson metadata
# MAGIC 4. Parsed skill scores from assessments
# MAGIC 5. Created user profiles using window functions
# MAGIC
# MAGIC **Next:** Run `03_gold_layer` for analytics aggregates and MLflow demo.
