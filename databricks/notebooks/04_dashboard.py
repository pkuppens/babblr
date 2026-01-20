# Databricks notebook source
# MAGIC %md
# MAGIC # Babblr Learning Analytics Dashboard
# MAGIC
# MAGIC This notebook provides an interactive dashboard for monitoring student progress, lesson effectiveness, and learning patterns.
# MAGIC
# MAGIC **Dashboard Sections:**
# MAGIC 1. Executive Summary KPIs
# MAGIC 2. Learning Activity Trends
# MAGIC 3. CEFR Level Distribution
# MAGIC 4. Lesson Effectiveness
# MAGIC 5. Student Segments
# MAGIC 6. Topic Engagement

# COMMAND ----------

# MAGIC %md
# MAGIC ## Executive Summary

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Key Performance Indicators
# MAGIC SELECT
# MAGIC     'Total Users' as metric,
# MAGIC     COUNT(DISTINCT user_id) as value
# MAGIC FROM babblr_silver.user_profiles
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC     'Total Conversations',
# MAGIC     COUNT(*)
# MAGIC FROM babblr_silver.conversations
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC     'Completed Lessons',
# MAGIC     COUNT(*)
# MAGIC FROM babblr_silver.lesson_progress
# MAGIC WHERE status = 'completed'
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC     'Assessment Attempts',
# MAGIC     COUNT(*)
# MAGIC FROM babblr_silver.assessment_attempts
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC     'Avg Assessment Score',
# MAGIC     ROUND(AVG(score), 1)
# MAGIC FROM babblr_silver.assessment_attempts

# COMMAND ----------

# MAGIC %md
# MAGIC ## Daily Active Users Trend
# MAGIC
# MAGIC *Tip: In Databricks, click the chart icon below the table to create a visualization*

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Daily Active Users (DAU)
# MAGIC SELECT
# MAGIC     activity_date,
# MAGIC     SUM(active_users) as daily_active_users,
# MAGIC     SUM(conversations) as daily_conversations
# MAGIC FROM babblr_gold.daily_metrics
# MAGIC GROUP BY activity_date
# MAGIC ORDER BY activity_date

# COMMAND ----------

# MAGIC %md
# MAGIC **Visualization Settings:**
# MAGIC - Chart Type: Line
# MAGIC - X-axis: activity_date
# MAGIC - Y-axis: daily_active_users, daily_conversations

# COMMAND ----------

# MAGIC %md
# MAGIC ## Language Distribution

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Users and activity by language
# MAGIC SELECT
# MAGIC     language,
# MAGIC     COUNT(DISTINCT user_id) as users,
# MAGIC     SUM(total_assessments) as assessments,
# MAGIC     ROUND(AVG(avg_score), 1) as avg_score
# MAGIC FROM babblr_silver.user_profiles
# MAGIC GROUP BY language
# MAGIC ORDER BY users DESC

# COMMAND ----------

# MAGIC %md
# MAGIC **Visualization Settings:**
# MAGIC - Chart Type: Bar
# MAGIC - X-axis: language
# MAGIC - Y-axis: users

# COMMAND ----------

# MAGIC %md
# MAGIC ## CEFR Level Funnel
# MAGIC
# MAGIC Shows student distribution across proficiency levels.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- CEFR level distribution (all languages)
# MAGIC SELECT
# MAGIC     cefr_level,
# MAGIC     SUM(users_at_level) as total_users,
# MAGIC     ROUND(AVG(avg_assessment_score), 1) as avg_score
# MAGIC FROM babblr_gold.cefr_funnel
# MAGIC GROUP BY cefr_level
# MAGIC ORDER BY
# MAGIC     CASE cefr_level
# MAGIC         WHEN 'A1' THEN 1
# MAGIC         WHEN 'A2' THEN 2
# MAGIC         WHEN 'B1' THEN 3
# MAGIC         WHEN 'B2' THEN 4
# MAGIC         WHEN 'C1' THEN 5
# MAGIC         WHEN 'C2' THEN 6
# MAGIC     END

# COMMAND ----------

# MAGIC %md
# MAGIC **Visualization Settings:**
# MAGIC - Chart Type: Funnel or Bar
# MAGIC - X-axis: cefr_level
# MAGIC - Y-axis: total_users

# COMMAND ----------

# MAGIC %md
# MAGIC ## Lesson Effectiveness Analysis
# MAGIC
# MAGIC Which lessons produce the best learning outcomes?

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Top lessons by effectiveness score
# MAGIC SELECT
# MAGIC     lesson_type,
# MAGIC     subject,
# MAGIC     lesson_difficulty,
# MAGIC     total_attempts,
# MAGIC     ROUND(completion_rate * 100, 1) as completion_rate_pct,
# MAGIC     ROUND(avg_mastery * 100, 1) as avg_mastery_pct,
# MAGIC     ROUND(effectiveness_score * 100, 1) as effectiveness_pct
# MAGIC FROM babblr_gold.lesson_effectiveness
# MAGIC ORDER BY effectiveness_score DESC
# MAGIC LIMIT 15

# COMMAND ----------

# MAGIC %md
# MAGIC ### Effectiveness by Lesson Type

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Aggregate effectiveness by lesson type
# MAGIC SELECT
# MAGIC     lesson_type,
# MAGIC     COUNT(*) as lesson_count,
# MAGIC     SUM(total_attempts) as total_attempts,
# MAGIC     ROUND(AVG(completion_rate) * 100, 1) as avg_completion_rate,
# MAGIC     ROUND(AVG(avg_mastery) * 100, 1) as avg_mastery,
# MAGIC     ROUND(AVG(effectiveness_score) * 100, 1) as avg_effectiveness
# MAGIC FROM babblr_gold.lesson_effectiveness
# MAGIC GROUP BY lesson_type
# MAGIC ORDER BY avg_effectiveness DESC

# COMMAND ----------

# MAGIC %md
# MAGIC **Visualization Settings:**
# MAGIC - Chart Type: Bar (grouped)
# MAGIC - X-axis: lesson_type
# MAGIC - Y-axis: avg_completion_rate, avg_mastery

# COMMAND ----------

# MAGIC %md
# MAGIC ## Student Segment Analysis
# MAGIC
# MAGIC Understanding different learner profiles helps personalize the experience.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Student segments from K-Means clustering
# MAGIC SELECT
# MAGIC     uc.cluster,
# MAGIC     CASE uc.cluster
# MAGIC         WHEN 0 THEN 'High Performers'
# MAGIC         WHEN 1 THEN 'Active Learners'
# MAGIC         WHEN 2 THEN 'Struggling Students'
# MAGIC         WHEN 3 THEN 'Casual Users'
# MAGIC         ELSE 'Unknown'
# MAGIC     END as segment_name,
# MAGIC     COUNT(*) as user_count,
# MAGIC     ROUND(AVG(up.avg_score), 1) as avg_score,
# MAGIC     ROUND(AVG(up.total_assessments), 1) as avg_assessments
# MAGIC FROM babblr_gold.user_clusters uc
# MAGIC JOIN babblr_silver.user_profiles up ON uc.user_id = up.user_id
# MAGIC GROUP BY uc.cluster
# MAGIC ORDER BY uc.cluster

# COMMAND ----------

# MAGIC %md
# MAGIC **Visualization Settings:**
# MAGIC - Chart Type: Pie or Bar
# MAGIC - Values: user_count
# MAGIC - Labels: segment_name

# COMMAND ----------

# MAGIC %md
# MAGIC ### Segment Characteristics Deep Dive

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Detailed segment characteristics
# MAGIC WITH segment_stats AS (
# MAGIC     SELECT
# MAGIC         uc.cluster,
# MAGIC         up.user_id,
# MAGIC         up.avg_score,
# MAGIC         up.total_assessments,
# MAGIC         COALESCE(conv.conv_count, 0) as conversations,
# MAGIC         COALESCE(conv.avg_error_rate, 0) as error_rate,
# MAGIC         COALESCE(lp.completed, 0) as completed_lessons
# MAGIC     FROM babblr_gold.user_clusters uc
# MAGIC     JOIN babblr_silver.user_profiles up ON uc.user_id = up.user_id
# MAGIC     LEFT JOIN (
# MAGIC         SELECT user_id, COUNT(*) as conv_count, AVG(error_rate) as avg_error_rate
# MAGIC         FROM babblr_silver.conversations GROUP BY user_id
# MAGIC     ) conv ON up.user_id = conv.user_id
# MAGIC     LEFT JOIN (
# MAGIC         SELECT user_id, COUNT(*) as completed
# MAGIC         FROM babblr_silver.lesson_progress WHERE status = 'completed' GROUP BY user_id
# MAGIC     ) lp ON up.user_id = lp.user_id
# MAGIC )
# MAGIC SELECT
# MAGIC     cluster,
# MAGIC     COUNT(*) as users,
# MAGIC     ROUND(AVG(avg_score), 1) as avg_score,
# MAGIC     ROUND(AVG(conversations), 1) as avg_conversations,
# MAGIC     ROUND(AVG(error_rate) * 100, 1) as error_rate_pct,
# MAGIC     ROUND(AVG(completed_lessons), 1) as avg_completed_lessons
# MAGIC FROM segment_stats
# MAGIC GROUP BY cluster
# MAGIC ORDER BY cluster

# COMMAND ----------

# MAGIC %md
# MAGIC ## Topic Engagement Heatmap

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Topic engagement across languages
# MAGIC SELECT
# MAGIC     topic_id,
# MAGIC     language,
# MAGIC     conversation_count,
# MAGIC     ROUND(avg_duration_min, 1) as avg_duration
# MAGIC FROM babblr_gold.topic_engagement
# MAGIC ORDER BY conversation_count DESC
# MAGIC LIMIT 50

# COMMAND ----------

# MAGIC %md
# MAGIC **Visualization Settings:**
# MAGIC - Chart Type: Heatmap
# MAGIC - X-axis: language
# MAGIC - Y-axis: topic_id
# MAGIC - Values: conversation_count

# COMMAND ----------

# MAGIC %md
# MAGIC ### Most Engaging Topics

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Topics with highest engagement (session duration)
# MAGIC SELECT
# MAGIC     topic_id,
# MAGIC     SUM(conversation_count) as total_conversations,
# MAGIC     SUM(unique_users) as total_users,
# MAGIC     ROUND(AVG(avg_duration_min), 1) as avg_session_min,
# MAGIC     ROUND(AVG(avg_messages_per_conv), 1) as avg_messages
# MAGIC FROM babblr_gold.topic_engagement
# MAGIC GROUP BY topic_id
# MAGIC ORDER BY avg_session_min DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## Error Rate Analysis
# MAGIC
# MAGIC Which CEFR levels have the highest error rates?

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Error rates by CEFR level
# MAGIC SELECT
# MAGIC     difficulty_level as cefr_level,
# MAGIC     COUNT(*) as conversations,
# MAGIC     ROUND(AVG(error_rate) * 100, 2) as avg_error_rate_pct,
# MAGIC     ROUND(AVG(message_count), 1) as avg_messages
# MAGIC FROM babblr_silver.conversations
# MAGIC GROUP BY difficulty_level
# MAGIC ORDER BY
# MAGIC     CASE difficulty_level
# MAGIC         WHEN 'A1' THEN 1
# MAGIC         WHEN 'A2' THEN 2
# MAGIC         WHEN 'B1' THEN 3
# MAGIC         WHEN 'B2' THEN 4
# MAGIC         WHEN 'C1' THEN 5
# MAGIC         WHEN 'C2' THEN 6
# MAGIC     END

# COMMAND ----------

# MAGIC %md
# MAGIC ## Assessment Performance Trends

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Weekly assessment performance
# MAGIC SELECT
# MAGIC     DATE_TRUNC('week', started_at) as week,
# MAGIC     COUNT(*) as assessments,
# MAGIC     ROUND(AVG(score), 1) as avg_score,
# MAGIC     COUNT(DISTINCT user_id) as unique_users
# MAGIC FROM babblr_silver.assessment_attempts
# MAGIC GROUP BY DATE_TRUNC('week', started_at)
# MAGIC ORDER BY week

# COMMAND ----------

# MAGIC %md
# MAGIC **Visualization Settings:**
# MAGIC - Chart Type: Combo (line + bar)
# MAGIC - X-axis: week
# MAGIC - Y-axis (left): assessments (bar)
# MAGIC - Y-axis (right): avg_score (line)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating a Databricks Dashboard
# MAGIC
# MAGIC To create a dashboard from these visualizations:
# MAGIC
# MAGIC 1. Click the **chart icon** below any SQL result to create a visualization
# MAGIC 2. Configure chart type and axes as noted above
# MAGIC 3. Click **Save** on the visualization
# MAGIC 4. Go to **Create** > **Dashboard**
# MAGIC 5. Click **Add** > **Visualization** and select from this notebook
# MAGIC 6. Arrange widgets as desired
# MAGIC
# MAGIC **Recommended Dashboard Layout:**
# MAGIC ```
# MAGIC ┌─────────────────────────────────────────────────────────┐
# MAGIC │  KPI Cards: Users | Conversations | Avg Score | Lessons │
# MAGIC ├─────────────────────────────┬───────────────────────────┤
# MAGIC │  Daily Active Users Trend   │  Language Distribution    │
# MAGIC ├─────────────────────────────┼───────────────────────────┤
# MAGIC │  CEFR Level Funnel          │  Student Segments Pie     │
# MAGIC ├─────────────────────────────┴───────────────────────────┤
# MAGIC │  Lesson Effectiveness Table                             │
# MAGIC ├─────────────────────────────────────────────────────────┤
# MAGIC │  Topic Engagement Heatmap                               │
# MAGIC └─────────────────────────────────────────────────────────┘
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC This dashboard provides insights for:
# MAGIC
# MAGIC | Stakeholder | Key Metrics |
# MAGIC |-------------|-------------|
# MAGIC | **Product Manager** | DAU, engagement trends, feature usage |
# MAGIC | **Content Team** | Lesson effectiveness, topic popularity |
# MAGIC | **Learning Designer** | Error patterns, CEFR progression |
# MAGIC | **Growth Team** | User segments, retention indicators |
# MAGIC
# MAGIC **Actionable Insights:**
# MAGIC 1. Focus content creation on high-engagement topics
# MAGIC 2. Improve or retire low-effectiveness lessons
# MAGIC 3. Create targeted interventions for "Struggling Students" segment
# MAGIC 4. Optimize CEFR advancement pace based on error rates

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC
# MAGIC ## Interview Talking Points
# MAGIC
# MAGIC When presenting this dashboard:
# MAGIC
# MAGIC 1. **Business Value**: "This dashboard helps the product team understand what's working and what needs improvement in the learning experience."
# MAGIC
# MAGIC 2. **Technical Depth**: "The data flows through a medallion architecture: Bronze (raw), Silver (cleaned/joined), Gold (aggregated). This ensures data quality and query performance."
# MAGIC
# MAGIC 3. **ML Integration**: "I used MLflow to track the student clustering experiment, which segments users for personalized interventions."
# MAGIC
# MAGIC 4. **Scalability**: "This architecture scales - we could add real-time streaming, more sophisticated ML models, or integrate with external data sources."
