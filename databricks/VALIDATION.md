# Databricks Tutorial - Validation Plan

> **GitHub Issue**: [#72 - Databricks Learning Analytics Tutorial](https://github.com/pkuppens/babblr/issues/72)

This document provides a comprehensive validation strategy and checklist for verifying the Databricks tutorial works correctly end-to-end.

## Validation Strategy

### Goals

1. **Functional Validation**: Verify all notebooks execute without errors
2. **Data Validation**: Confirm data flows correctly through Bronze → Silver → Gold layers
3. **User Experience Validation**: Ensure a complete beginner can follow the tutorial
4. **Use Case Validation**: Verify the analytics answer real business questions

### Approach

We validate at three levels:

| Level | What We Test | How |
|-------|--------------|-----|
| **Local** | Data generation, file creation | Run scripts locally, inspect outputs |
| **Databricks** | Notebooks, Delta tables, queries | Execute in Databricks workspace |
| **Use Case** | Business value, actionable insights | Role-play as "Training Material Manager" |

### Test Environment

- **Local**: Windows/Mac/Linux with Python 3.11+ (avoid 3.13 for PyTorch/CUDA compatibility)
- **Databricks**: [Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition) (serverless)
- **Data**: Synthetic data from `generate_synthetic_data.py`

> **Note**: Databricks Community Edition was [retired January 1, 2026](https://community.databricks.com/t5/announcements/psa-community-edition-retires-at-the-end-of-2025-move-to-free/td-p/141888).
> Free Edition uses **serverless compute** - no manual cluster creation required.

### Key Free Edition Characteristics

| Feature | Free Edition | Notes |
|---------|--------------|-------|
| Compute | Serverless (managed) | No cluster creation needed |
| Languages | Python, SQL | Scala/R not supported |
| Storage | Unity Catalog Volumes | DBFS root restricted |
| ML | MLflow, Model Serving | GPU support in beta |
| Limits | Daily quota | Resets next day if exceeded |

See: [Free Edition Limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)

---

## Pre-Validation Checklist

Before starting validation, ensure you have:

- [ ] Python 3.12 installed locally (the project uses Python 3.12)
- [ ] [uv](https://docs.astral.sh/uv/) installed (the project's package manager)
- [ ] Backend dependencies installed: `cd backend && uv sync`
- [ ] [Databricks Free Edition account](https://www.databricks.com/product/faq/community-edition) created
- [ ] All files from the `databricks/` folder available
- [ ] At least 2 hours available for full validation

> **Note**: The `pandas`, `pyarrow`, and `numpy` packages are included in the backend's `pyproject.toml` and will be installed by `uv sync`.

---

## Part 1: Local Validation

### 1.1 Data Generation Script

**Goal**: Verify `generate_synthetic_data.py` creates valid data files.

```bash
# Run from the backend directory to reuse the uv environment
cd backend
uv run python ../databricks/generate_synthetic_data.py --output-dir ../databricks/data
```

> **Note**: The data generation dependencies (`pandas`, `pyarrow`) are included in the backend's `pyproject.toml`.

**Checklist**:

- [ ] Script runs without errors
- [ ] Script prints progress messages
- [ ] `databricks/data/` folder is created (if not exists)
- [ ] All 7 parquet files are created:
  - [ ] `databricks/data/conversations.parquet`
  - [ ] `databricks/data/messages.parquet`
  - [ ] `databricks/data/lessons.parquet`
  - [ ] `databricks/data/lesson_progress.parquet`
  - [ ] `databricks/data/assessments.parquet`
  - [ ] `databricks/data/assessment_attempts.parquet`
  - [ ] `databricks/data/user_levels.parquet`
- [ ] Total file size is approximately 150-200 KB
- [ ] Running script again with same seed produces identical files

**Data Spot Checks** (run from the backend directory):

```bash
cd backend
uv run python -c "
import pandas as pd

# Check conversations
df = pd.read_parquet('../databricks/data/conversations.parquet')
print(f'Conversations: {len(df)} rows')
assert len(df) > 400, 'Expected 400+ conversations'
assert 'user_id' in df.columns
assert 'language' in df.columns
assert df['language'].nunique() == 6, 'Expected 6 languages'

# Check messages
df = pd.read_parquet('../databricks/data/messages.parquet')
print(f'Messages: {len(df)} rows')
assert len(df) > 2000, 'Expected 2000+ messages'

# Check assessments catalog
df = pd.read_parquet('../databricks/data/assessments.parquet')
print(f'Assessments: {len(df)} rows')
assert len(df) == 144, 'Expected 144 assessment definitions'

# Check assessment attempts
df = pd.read_parquet('../databricks/data/assessment_attempts.parquet')
print(f'Assessment attempts: {len(df)} rows')
assert len(df) > 150, 'Expected 150+ attempts'

print('All local data checks passed!')
"
```

- [ ] All assertions pass
- [ ] Row counts match expected ranges

### 1.2 Notebook File Validation

**Goal**: Verify notebook files are valid JSON, can be opened, and have correct structure.  
**Note**: This section only validates file structure and syntax. Actual execution testing happens in Part 2 (Databricks Validation), as these notebooks require Databricks runtime and storage.

**Checklist**:

- [ ] `01_bronze_layer.ipynb` opens in VS Code/JupyterLab without errors
- [ ] `02_silver_layer.ipynb` opens without errors
- [ ] `03_gold_layer.ipynb` opens without errors
- [ ] `04_dashboard.ipynb` opens without errors
- [ ] Each notebook has markdown cells with explanations
- [ ] Each notebook has code cells with Python/SQL code
- [ ] Python code syntax is valid (can be checked with a linter or syntax checker)
- [ ] No `# MAGIC` or `# COMMAND ----------` syntax remains (Databricks format)
- [ ] Notebooks are ready for import into Databricks (valid JSON structure)

> **Note**: These notebooks are designed to run in Databricks and will not execute successfully locally due to dependencies on Databricks runtime (Spark, Delta Lake, Unity Catalog). Execution validation is performed in Part 2.

### 1.3 README Validation

**Goal**: Verify documentation is complete and accurate.

**Checklist**:

- [ ] README.md renders correctly on GitHub (or in VS Code preview)
- [ ] All internal links work (e.g., #troubleshooting)
- [ ] Prerequisites section lists all requirements
- [ ] All code blocks have correct syntax highlighting
- [ ] Folder structure matches actual files
- [ ] No broken external links

---

## Part 2: Databricks Validation

### 2.1 Account and Serverless Compute Setup

**Goal**: Verify Databricks Free Edition environment is ready.

**Documentation**: [Sign up for Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition)

**Account Creation Checklist**:

- [ ] Navigate to [databricks.com/try-databricks](https://www.databricks.com/try-databricks)
- [ ] Click "Try Databricks Free"
- [ ] Sign up with email, Google, or Microsoft account
- [ ] Verify email if required
- [ ] Workspace URL is accessible (e.g., `https://adb-xxxxx.azuredatabricks.net/`)

**Workspace Verification**:

- [ ] Can log into Databricks workspace
- [ ] Workspace loads without errors
- [ ] Left sidebar shows: Workspace, Catalog, Workflows, Compute, etc.
- [ ] Unity Catalog is enabled (required for serverless)

**Serverless Compute Verification**:

> **Note**: Free Edition uses [serverless compute](https://docs.databricks.com/aws/en/compute/serverless/notebooks) -
> you don't create clusters manually. Databricks manages compute for you.

- [ ] Open any notebook
- [ ] Click **"Connect"** dropdown (top-right of notebook)
- [ ] **"Serverless"** option is available
- [ ] Can connect to Serverless compute
- [ ] Compute starts within 30 seconds (no 5-10 min cluster startup)

### 2.2 File Upload

**Goal**: Verify data files can be uploaded.

**Documentation**: [Import notebooks](https://docs.databricks.com/aws/en/notebooks/notebook-export-import) | [Upload to volumes](https://docs.databricks.com/aws/en/ingestion/file-upload/upload-to-volume)

**Notebook Import Checklist**:

- [ ] Click **Workspace** in sidebar
- [ ] Right-click folder → **Import** (or use kebab menu → Import)
- [ ] Can import all 4 `.ipynb` notebook files
- [ ] Notebooks appear in the folder after import
- [ ] Can open each notebook in the Databricks editor
- [ ] Can connect notebooks to **Serverless** compute

**Data Upload via Unity Catalog Volumes** (recommended):

> **Documentation**: [Work with files in volumes](https://docs.databricks.com/aws/en/volumes/volume-files)

- [ ] Click **Catalog** in sidebar
- [ ] Navigate to or create catalog (e.g., `main` or `hive_metastore`)
- [ ] Create schema: **Create** → **Schema** → name it `babblr`
- [ ] Create volume: Click schema → **Create** → **Volume** → name it `bronze`
- [ ] Click **"Add"** or **"Upload"** in the volume
- [ ] Upload all 7 parquet files (max 5GB per file)
- [ ] Files appear in `/Volumes/<catalog>/babblr/bronze/`

**Alternative - Data Upload via Notebook UI**:

- [ ] Open a notebook
- [ ] Click the **paperclip icon** or **"Upload Data"** button
- [ ] Upload parquet files
- [ ] Note the path shown after upload (typically `/tmp/` or workspace path)
- [ ] Update notebook `BRONZE_PATH` variable to match

### 2.3 Notebook 01: Bronze Layer

**Goal**: Verify raw data ingestion works.

**Pre-conditions**:
- Connected to Serverless compute (click **Connect** → **Serverless**)
- Data files are uploaded to Unity Catalog volume
- Notebook is open in Databricks editor

**Execution Checklist**:

- [ ] Cell 1 (Setup): Runs without errors
- [ ] Correct storage path is detected and printed
- [ ] Database `babblr_bronze` is created
- [ ] Cell 2 (List files): Shows all 7 parquet files
- [ ] Cell 3 (load_to_delta function): Runs without errors
- [ ] Cell 4 (Load all tables): All 7 tables load successfully
- [ ] Output shows row counts for each table:
  - [ ] `conversations`: 400+ rows
  - [ ] `messages`: 2000+ rows
  - [ ] `lessons`: 50+ rows
  - [ ] `lesson_progress`: 800+ rows
  - [ ] `assessments`: 144 rows
  - [ ] `assessment_attempts`: 150+ rows
  - [ ] `user_levels`: 50 rows
- [ ] `SHOW TABLES` displays all 7 tables
- [ ] `SELECT * FROM conversations LIMIT 5` returns data
- [ ] Language distribution query shows 6 languages
- [ ] `DESCRIBE HISTORY conversations` shows table history
- [ ] `DESCRIBE TABLE EXTENDED conversations` shows schema

**Post-conditions**:
- [ ] All tables exist in `babblr_bronze` database
- [ ] No error messages in any cell output

### 2.4 Notebook 02: Silver Layer

**Goal**: Verify data cleaning and transformation works.

**Pre-conditions**:
- Notebook 01 completed successfully
- Bronze tables exist

**Execution Checklist**:

- [ ] Cell 1 (Setup): Creates `babblr_silver` database
- [ ] Cell 2 (Clean conversations):
  - [ ] Joins with messages successfully
  - [ ] Calculates `duration_minutes` and `error_rate`
  - [ ] Row count matches bronze conversations
- [ ] Preview shows cleaned data with new columns
- [ ] Cell 3 (Parse corrections):
  - [ ] JSON parsing works without errors
  - [ ] `error_count` column is populated
  - [ ] Query for `error_count > 0` returns results
- [ ] Cell 4 (Lesson progress):
  - [ ] Joins with lessons table
  - [ ] `time_to_complete_hours` is calculated
  - [ ] Completion stats by type shows data
- [ ] Cell 5 (Assessment attempts):
  - [ ] Skill scores JSON is parsed
  - [ ] `duration_minutes` is calculated
  - [ ] Performance by type query returns data
- [ ] Cell 6 (User profiles):
  - [ ] Window functions execute without errors
  - [ ] User profiles are aggregated correctly
  - [ ] Preview shows user-level statistics
- [ ] Data quality summary shows row counts for all 5 silver tables

**Post-conditions**:
- [ ] All tables exist in `babblr_silver` database
- [ ] Silver tables have more columns than bronze (enriched)

### 2.5 Notebook 03: Gold Layer

**Goal**: Verify analytics aggregates and MLflow work.

**Documentation**: [MLflow tracking](https://docs.databricks.com/aws/en/mlflow/tracking) | [MLflow experiments](https://docs.databricks.com/aws/en/mlflow/experiments)

**Pre-conditions**:
- Notebook 02 completed successfully
- Silver tables exist
- Connected to Serverless compute

**Execution Checklist**:

- [ ] Cell 1 (Setup): Creates `babblr_gold` database
- [ ] Cell 2 (Daily metrics):
  - [ ] Aggregation query runs without errors
  - [ ] `daily_metrics` table is created
  - [ ] Preview shows dates, languages, active users
- [ ] Cell 3 (Lesson effectiveness):
  - [ ] CTE query executes successfully
  - [ ] `effectiveness_score` is calculated
  - [ ] Top 10 query shows ranked lessons
- [ ] Cell 4 (CEFR funnel):
  - [ ] CEFR levels are ordered correctly (A1→C2)
  - [ ] Spanish funnel data is visible
- [ ] Cell 5 (Topic engagement):
  - [ ] Topic aggregates are created
  - [ ] Most engaging topics query returns results
- [ ] Cell 6 (MLflow clustering):
  - [ ] `mlflow.set_experiment()` succeeds
  - [ ] User features query returns 50 users
  - [ ] K-Means model trains without errors
  - [ ] MLflow logs parameters (k_clusters, features)
  - [ ] MLflow logs metrics (inertia, cluster sizes)
  - [ ] Model is saved to MLflow
  - [ ] Cluster statistics show 4 clusters
  - [ ] Cluster analysis displays user segments
- [ ] Cell 7 (Save clusters):
  - [ ] `user_clusters` table is created
  - [ ] 50 user assignments are saved
- [ ] Gold layer summary shows 5 tables with row counts

**Post-conditions**:
- [ ] All tables exist in `babblr_gold` database
- [ ] MLflow experiment is visible in Experiments tab
- [ ] Experiment contains logged run with parameters and metrics

### 2.6 Notebook 04: Dashboard

**Goal**: Verify visualizations and dashboard queries work.

**Pre-conditions**:
- Notebook 03 completed successfully
- All Gold tables exist

**Execution Checklist**:

- [ ] KPI query returns 5 metrics (users, conversations, lessons, attempts, avg score)
- [ ] Daily active users query returns date-ordered data
- [ ] Language distribution query shows 6 languages
- [ ] CEFR funnel query shows levels A1-C2
- [ ] Lesson effectiveness query shows top 15 lessons
- [ ] Effectiveness by type shows 3 lesson types
- [ ] Student segments query shows 4 clusters with names
- [ ] Segment deep dive shows detailed characteristics
- [ ] Topic engagement heatmap data is available
- [ ] Most engaging topics shows top 10
- [ ] Error rate by CEFR level shows expected pattern
- [ ] Weekly assessment trends show time series data

**Visualization Checklist** (create at least 2):

- [ ] Can click chart icon below a query result
- [ ] Can select chart type (bar, line, pie)
- [ ] Can configure X and Y axes
- [ ] Chart renders correctly
- [ ] Can save visualization

**Dashboard Creation** (optional):

- [ ] Can create new dashboard from menu
- [ ] Can add saved visualizations to dashboard
- [ ] Dashboard displays multiple charts
- [ ] Dashboard can be shared/published

---

## Part 3: Use Case Validation

### Use Case: Training Material Manager

**Persona**: Sarah, a Training Material Manager at Babblr. She needs to identify which lessons and assessments need improvement based on student performance data.

**Goal**: Validate that the analytics pipeline provides actionable insights for improving training materials.

### 3.1 Scenario: Identify Underperforming Lessons

**Task**: Find lessons with low completion rates or low mastery scores.

**Steps**:

1. Open notebook 04 or run SQL directly
2. Execute the lesson effectiveness query

**Validation Queries**:

```sql
-- Find lessons with completion rate below 60%
SELECT
    lesson_type,
    subject,
    lesson_difficulty,
    total_attempts,
    ROUND(completion_rate * 100, 1) as completion_rate_pct,
    ROUND(avg_mastery * 100, 1) as avg_mastery_pct
FROM babblr_gold.lesson_effectiveness
WHERE completion_rate < 0.6
ORDER BY completion_rate ASC;
```

**Checklist**:

- [ ] Query executes without errors
- [ ] Results show lessons with low completion rates
- [ ] Can identify specific subjects that need attention
- [ ] Can compare performance across lesson types (vocab, grammar, listening)
- [ ] Data supports decision: "We should redesign lessons X, Y, Z"

### 3.2 Scenario: Identify Struggling Student Segments

**Task**: Find which student segments need additional support.

**Steps**:

1. Review the student clusters from MLflow analysis
2. Examine detailed segment characteristics

**Validation Queries**:

```sql
-- Find the "Struggling Students" segment details
SELECT
    uc.cluster,
    CASE uc.cluster
        WHEN 0 THEN 'High Performers'
        WHEN 1 THEN 'Active Learners'
        WHEN 2 THEN 'Struggling Students'
        WHEN 3 THEN 'Casual Users'
    END as segment_name,
    COUNT(*) as user_count,
    ROUND(AVG(up.avg_score), 1) as avg_score,
    ROUND(AVG(up.total_assessments), 1) as avg_assessments
FROM babblr_gold.user_clusters uc
JOIN babblr_silver.user_profiles up ON uc.user_id = up.user_id
GROUP BY uc.cluster
ORDER BY avg_score ASC;
```

**Checklist**:

- [ ] Query identifies distinct student segments
- [ ] "Struggling Students" segment has lower avg_score
- [ ] Can quantify how many students are in each segment
- [ ] Can identify characteristics of struggling students (high error rate, few completed lessons)
- [ ] Data supports decision: "We need intervention for X% of students"

### 3.3 Scenario: Analyze Assessment Difficulty

**Task**: Determine if assessments are appropriately calibrated for each CEFR level.

**Validation Queries**:

```sql
-- Check if assessment scores align with expected difficulty
SELECT
    assessment_difficulty,
    COUNT(*) as attempts,
    ROUND(AVG(score), 1) as avg_score,
    ROUND(STDDEV(score), 1) as score_stddev,
    ROUND(AVG(duration_minutes), 1) as avg_duration
FROM babblr_silver.assessment_attempts
GROUP BY assessment_difficulty
ORDER BY
    CASE assessment_difficulty
        WHEN 'A1' THEN 1 WHEN 'A2' THEN 2
        WHEN 'B1' THEN 3 WHEN 'B2' THEN 4
        WHEN 'C1' THEN 5 WHEN 'C2' THEN 6
    END;
```

**Checklist**:

- [ ] Query shows scores by CEFR level
- [ ] A1/A2 levels have higher average scores (easier)
- [ ] C1/C2 levels have lower average scores (harder)
- [ ] Score distribution makes sense (stddev reasonable)
- [ ] Duration increases with difficulty (harder = longer)
- [ ] Can identify if any level is miscalibrated
- [ ] Data supports decision: "B2 assessments may be too easy, need review"

### 3.4 Scenario: Track Content Engagement

**Task**: Identify which conversation topics are most/least engaging.

**Validation Queries**:

```sql
-- Find topics with highest and lowest engagement
SELECT
    topic_id,
    SUM(conversation_count) as total_conversations,
    ROUND(AVG(avg_duration_min), 1) as avg_session_minutes,
    ROUND(AVG(avg_messages_per_conv), 1) as avg_messages,
    ROUND(AVG(avg_error_rate) * 100, 1) as avg_error_rate_pct
FROM babblr_gold.topic_engagement
GROUP BY topic_id
ORDER BY avg_session_minutes DESC;
```

**Checklist**:

- [ ] Query shows engagement metrics by topic
- [ ] Can identify most engaging topics (longest sessions)
- [ ] Can identify least engaging topics (shortest sessions)
- [ ] Error rates vary by topic (some topics harder than others)
- [ ] Data supports decision: "Create more content around topic X, less around Y"

### 3.5 Summary: Training Material Manager Decisions

After completing the use case validation, the Training Material Manager should be able to make these data-driven decisions:

| Decision | Data Source | Example Insight |
|----------|-------------|-----------------|
| Which lessons to redesign | `lesson_effectiveness` | "Grammar/subjunctive has 45% completion, needs simplification" |
| Which students need help | `user_clusters` | "23% of students are in 'Struggling' segment" |
| Assessment calibration | `assessment_attempts` | "B2 assessments have 85% avg score, may be too easy" |
| Content prioritization | `topic_engagement` | "Travel topics have 12min avg session, expand this area" |
| Learning velocity | `cefr_funnel` | "Students progress from A1→A2 in 3 weeks on average" |
| At-risk detection | Segment characteristics | "High error rate + few lessons = intervention needed" |

**Final Use Case Checklist**:

- [ ] All four scenarios executed successfully
- [ ] Each scenario produced actionable insights
- [ ] Data quality sufficient for decision-making
- [ ] Results are reproducible (same data = same insights)
- [ ] Training Material Manager persona validated

---

## Part 4: Error Recovery Validation

### 4.1 Common Error Scenarios

Test that the tutorial handles errors gracefully.

**Scenario: Missing Data Files**

- [ ] If parquet files not uploaded, notebook shows clear error message
- [ ] Error message includes instructions for uploading files
- [ ] Notebook doesn't crash with cryptic Spark errors

**Scenario: Serverless Compute Issues**

- [ ] Notebooks prompt to connect if not connected
- [ ] Can reconnect to Serverless if session times out
- [ ] Session state is restored after reconnection (variables preserved)
- [ ] Clear message if daily quota exceeded (resets next day)

**Scenario: Database Already Exists**

- [ ] `CREATE DATABASE IF NOT EXISTS` doesn't fail
- [ ] Re-running notebooks overwrites tables cleanly
- [ ] No duplicate table errors

**Scenario: MLflow Experiment Exists**

- [ ] `mlflow.set_experiment()` works even if experiment exists
- [ ] New runs are added to existing experiment
- [ ] No permission errors

### 4.2 Recovery Procedures

- [ ] Can re-run any notebook from the beginning
- [ ] Can re-run individual cells without issues
- [ ] Tables can be dropped and recreated
- [ ] MLflow runs can be deleted if needed

---

## Validation Sign-Off

### Summary

| Section | Status | Notes |
|---------|--------|-------|
| Part 1: Local Validation | [ ] Pass / [ ] Fail | |
| Part 2: Databricks Validation | [ ] Pass / [ ] Fail | |
| Part 3: Use Case Validation | [ ] Pass / [ ] Fail | |
| Part 4: Error Recovery | [ ] Pass / [ ] Fail | |

### Validation Completed By

- **Name**: _________________________
- **Date**: _________________________
- **GitHub Issue**: [#72](https://github.com/pkuppens/babblr/issues/72)
- **Databricks Workspace URL**: _________________________
- **Data Generation Seed Used**: 42 (default)

### Issues Found

| Issue | Severity | Resolution |
|-------|----------|------------|
| | | |
| | | |
| | | |

### Final Approval

- [ ] All critical tests passed
- [ ] Tutorial is ready for beginner users
- [ ] Use case provides actionable business insights
- [ ] Documentation matches actual behavior

**Approved**: [ ] Yes / [ ] No

**Approver Signature**: _________________________
