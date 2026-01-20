# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer - Analytics & MLflow
# MAGIC
# MAGIC This notebook creates business-ready aggregates and demonstrates MLflow experiment tracking.
# MAGIC
# MAGIC **Key Concepts:**
# MAGIC - Gold layer aggregations
# MAGIC - Complex SQL analytics
# MAGIC - MLflow experiment tracking
# MAGIC - K-Means clustering for student segmentation

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window
import mlflow
import mlflow.spark

# Configuration
SILVER_DB = "babblr_silver"
GOLD_DB = "babblr_gold"

# Create gold database
spark.sql(f"CREATE DATABASE IF NOT EXISTS {GOLD_DB}")
print(f"Gold database: {GOLD_DB}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Daily Learning Metrics
# MAGIC
# MAGIC Aggregate daily metrics for dashboard KPIs.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE babblr_gold.daily_metrics AS
# MAGIC SELECT
# MAGIC     DATE(created_at) as activity_date,
# MAGIC     language,
# MAGIC     COUNT(DISTINCT user_id) as active_users,
# MAGIC     COUNT(*) as conversations,
# MAGIC     SUM(message_count) as total_messages,
# MAGIC     ROUND(AVG(duration_minutes), 1) as avg_session_minutes,
# MAGIC     ROUND(AVG(error_rate), 3) as avg_error_rate
# MAGIC FROM babblr_silver.conversations
# MAGIC GROUP BY DATE(created_at), language
# MAGIC ORDER BY activity_date, language

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Preview daily metrics
# MAGIC SELECT * FROM babblr_gold.daily_metrics
# MAGIC ORDER BY activity_date DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Lesson Effectiveness Scores
# MAGIC
# MAGIC Calculate which lessons lead to the best learning outcomes.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE babblr_gold.lesson_effectiveness AS
# MAGIC WITH lesson_stats AS (
# MAGIC     SELECT
# MAGIC         lesson_id,
# MAGIC         lesson_type,
# MAGIC         subject,
# MAGIC         lesson_difficulty,
# MAGIC         COUNT(*) as total_attempts,
# MAGIC         SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completions,
# MAGIC         AVG(CASE WHEN status = 'completed' THEN mastery_score END) as avg_mastery,
# MAGIC         AVG(time_to_complete_hours) as avg_completion_time
# MAGIC     FROM babblr_silver.lesson_progress
# MAGIC     GROUP BY lesson_id, lesson_type, subject, lesson_difficulty
# MAGIC )
# MAGIC SELECT
# MAGIC     *,
# MAGIC     ROUND(completions * 1.0 / total_attempts, 3) as completion_rate,
# MAGIC     -- Effectiveness score: weighted combination of completion rate and mastery
# MAGIC     ROUND(
# MAGIC         (completions * 1.0 / total_attempts) * 0.4 +
# MAGIC         COALESCE(avg_mastery, 0) * 0.6,
# MAGIC         3
# MAGIC     ) as effectiveness_score
# MAGIC FROM lesson_stats
# MAGIC WHERE total_attempts >= 3

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Top 10 most effective lessons
# MAGIC SELECT
# MAGIC     lesson_type,
# MAGIC     subject,
# MAGIC     lesson_difficulty,
# MAGIC     total_attempts,
# MAGIC     completion_rate,
# MAGIC     ROUND(avg_mastery, 3) as avg_mastery,
# MAGIC     effectiveness_score
# MAGIC FROM babblr_gold.lesson_effectiveness
# MAGIC ORDER BY effectiveness_score DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. CEFR Level Progression Funnel
# MAGIC
# MAGIC Track how students progress through CEFR levels.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE babblr_gold.cefr_funnel AS
# MAGIC SELECT
# MAGIC     language,
# MAGIC     recommended_level as cefr_level,
# MAGIC     COUNT(DISTINCT user_id) as users_at_level,
# MAGIC     ROUND(AVG(score), 1) as avg_assessment_score,
# MAGIC     COUNT(*) as total_assessments
# MAGIC FROM babblr_silver.assessment_attempts
# MAGIC GROUP BY language, recommended_level
# MAGIC ORDER BY language,
# MAGIC     CASE recommended_level
# MAGIC         WHEN 'A1' THEN 1
# MAGIC         WHEN 'A2' THEN 2
# MAGIC         WHEN 'B1' THEN 3
# MAGIC         WHEN 'B2' THEN 4
# MAGIC         WHEN 'C1' THEN 5
# MAGIC         WHEN 'C2' THEN 6
# MAGIC     END

# COMMAND ----------

# MAGIC %sql
# MAGIC -- CEFR funnel visualization data
# MAGIC SELECT * FROM babblr_gold.cefr_funnel
# MAGIC WHERE language = 'spanish'

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Topic Engagement Analysis

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE babblr_gold.topic_engagement AS
# MAGIC SELECT
# MAGIC     topic_id,
# MAGIC     language,
# MAGIC     COUNT(*) as conversation_count,
# MAGIC     COUNT(DISTINCT user_id) as unique_users,
# MAGIC     ROUND(AVG(message_count), 1) as avg_messages_per_conv,
# MAGIC     ROUND(AVG(duration_minutes), 1) as avg_duration_min,
# MAGIC     ROUND(AVG(error_rate), 3) as avg_error_rate
# MAGIC FROM babblr_silver.conversations
# MAGIC WHERE topic_id IS NOT NULL
# MAGIC GROUP BY topic_id, language

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Most engaging topics (by session duration)
# MAGIC SELECT
# MAGIC     topic_id,
# MAGIC     SUM(conversation_count) as total_conversations,
# MAGIC     ROUND(AVG(avg_duration_min), 1) as avg_duration,
# MAGIC     ROUND(AVG(avg_messages_per_conv), 1) as avg_messages
# MAGIC FROM babblr_gold.topic_engagement
# MAGIC GROUP BY topic_id
# MAGIC ORDER BY avg_duration DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. MLflow: Student Clustering
# MAGIC
# MAGIC Demonstrate MLflow experiment tracking with K-Means clustering to segment students by learning patterns.

# COMMAND ----------

from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline

# Prepare features for clustering
user_features = spark.sql("""
    SELECT
        up.user_id,
        up.total_assessments,
        up.avg_score,
        COALESCE(up.avg_improvement, 0) as avg_improvement,
        up.proficiency_score,
        COALESCE(conv.total_conversations, 0) as total_conversations,
        COALESCE(conv.avg_error_rate, 0) as avg_error_rate,
        COALESCE(lp.completed_lessons, 0) as completed_lessons,
        COALESCE(lp.avg_mastery, 0) as avg_mastery
    FROM babblr_silver.user_profiles up
    LEFT JOIN (
        SELECT user_id, COUNT(*) as total_conversations, AVG(error_rate) as avg_error_rate
        FROM babblr_silver.conversations
        GROUP BY user_id
    ) conv ON up.user_id = conv.user_id
    LEFT JOIN (
        SELECT user_id, COUNT(*) as completed_lessons, AVG(mastery_score) as avg_mastery
        FROM babblr_silver.lesson_progress
        WHERE status = 'completed'
        GROUP BY user_id
    ) lp ON up.user_id = lp.user_id
""")

print(f"Users for clustering: {user_features.count()}")
user_features.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ### MLflow Experiment Setup

# COMMAND ----------

# Set experiment name
experiment_name = "/Shared/babblr_student_segmentation"
mlflow.set_experiment(experiment_name)

print(f"MLflow experiment: {experiment_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Train Clustering Model with MLflow Tracking

# COMMAND ----------

# Feature columns for clustering
feature_cols = [
    "total_assessments", "avg_score", "avg_improvement",
    "total_conversations", "avg_error_rate", "completed_lessons", "avg_mastery"
]

# Start MLflow run
with mlflow.start_run(run_name="student_clustering_v1"):

    # Log parameters
    k_clusters = 4
    mlflow.log_param("k_clusters", k_clusters)
    mlflow.log_param("features", feature_cols)
    mlflow.log_param("n_users", user_features.count())

    # Build pipeline
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features_raw")
    scaler = StandardScaler(inputCol="features_raw", outputCol="features", withStd=True, withMean=True)
    kmeans = KMeans(k=k_clusters, seed=42, featuresCol="features", predictionCol="cluster")

    pipeline = Pipeline(stages=[assembler, scaler, kmeans])

    # Fit model
    model = pipeline.fit(user_features)

    # Get predictions
    predictions = model.transform(user_features)

    # Calculate cluster metrics
    cluster_stats = predictions.groupBy("cluster").agg(
        F.count("*").alias("user_count"),
        F.round(F.avg("avg_score"), 1).alias("avg_score"),
        F.round(F.avg("total_conversations"), 1).alias("avg_conversations"),
        F.round(F.avg("completed_lessons"), 1).alias("avg_completed_lessons")
    ).orderBy("cluster")

    # Log metrics
    kmeans_model = model.stages[-1]
    mlflow.log_metric("inertia", kmeans_model.summary.trainingCost)

    for row in cluster_stats.collect():
        mlflow.log_metric(f"cluster_{row['cluster']}_size", row["user_count"])
        mlflow.log_metric(f"cluster_{row['cluster']}_avg_score", row["avg_score"])

    # Log model
    mlflow.spark.log_model(model, "student_clustering_model")

    print("Model training complete!")
    print(f"Inertia (within-cluster sum of squares): {kmeans_model.summary.trainingCost:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Cluster Analysis

# COMMAND ----------

# Show cluster statistics
cluster_stats.show()

# COMMAND ----------

# Analyze cluster characteristics
cluster_analysis = predictions.groupBy("cluster").agg(
    F.count("*").alias("users"),
    F.round(F.avg("avg_score"), 1).alias("avg_assessment_score"),
    F.round(F.avg("avg_error_rate"), 3).alias("avg_error_rate"),
    F.round(F.avg("completed_lessons"), 1).alias("avg_lessons_completed"),
    F.round(F.avg("avg_mastery"), 3).alias("avg_mastery_score")
).orderBy("cluster")

display(cluster_analysis)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Interpret Clusters
# MAGIC
# MAGIC Based on the cluster characteristics, we can label them:
# MAGIC - **Cluster 0**: High performers (high scores, many completed lessons)
# MAGIC - **Cluster 1**: Active learners (many conversations, moderate scores)
# MAGIC - **Cluster 2**: Struggling students (high error rates, lower scores)
# MAGIC - **Cluster 3**: Casual users (low engagement, few assessments)

# COMMAND ----------

# Save cluster assignments to gold layer
cluster_assignments = predictions.select("user_id", "cluster")
cluster_assignments.write.format("delta").mode("overwrite").saveAsTable(f"{GOLD_DB}.user_clusters")

print(f"Saved {cluster_assignments.count()} user cluster assignments")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Gold Layer Summary

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Summary of gold layer tables
# MAGIC SELECT 'daily_metrics' as table_name, COUNT(*) as row_count FROM babblr_gold.daily_metrics
# MAGIC UNION ALL
# MAGIC SELECT 'lesson_effectiveness', COUNT(*) FROM babblr_gold.lesson_effectiveness
# MAGIC UNION ALL
# MAGIC SELECT 'cefr_funnel', COUNT(*) FROM babblr_gold.cefr_funnel
# MAGIC UNION ALL
# MAGIC SELECT 'topic_engagement', COUNT(*) FROM babblr_gold.topic_engagement
# MAGIC UNION ALL
# MAGIC SELECT 'user_clusters', COUNT(*) FROM babblr_gold.user_clusters

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC In this notebook we:
# MAGIC 1. Created daily metrics aggregates
# MAGIC 2. Calculated lesson effectiveness scores
# MAGIC 3. Built CEFR progression funnel
# MAGIC 4. Analyzed topic engagement
# MAGIC 5. **Trained K-Means clustering with MLflow tracking**
# MAGIC
# MAGIC **MLflow Benefits Demonstrated:**
# MAGIC - Parameter logging
# MAGIC - Metric tracking
# MAGIC - Model versioning
# MAGIC - Reproducible experiments
# MAGIC
# MAGIC **Next:** Run `04_dashboard` for visualizations.
