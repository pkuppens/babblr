# Babblr Learning Analytics - Databricks Tutorial

A hands-on tutorial for learning Databricks through building a learning analytics pipeline.

## What You'll Learn

By completing this tutorial, you will understand:

| Concept | What It Is | Where You'll Use It |
|---------|------------|---------------------|
| **Databricks Workspace** | Your main interface for data engineering | Throughout |
| **Delta Lake** | Storage format with versioning and transactions | All notebooks |
| **Medallion Architecture** | Bronze/Silver/Gold data organization pattern | Notebooks 01-03 |
| **Spark SQL** | SQL for big data processing | All notebooks |
| **MLflow** | Machine learning experiment tracking | Notebook 03 |
| **Dashboards** | Data visualization in Databricks | Notebook 04 |

**Time to complete:** 2-3 hours (including account setup)

---

## Prerequisites

Before starting, make sure you have:

- [ ] **Python 3.8+** installed locally ([download](https://www.python.org/downloads/))
- [ ] **pandas** and **numpy** packages (`pip install pandas numpy`)
- [ ] A **web browser** (Chrome, Firefox, or Edge recommended)
- [ ] Basic familiarity with SQL (SELECT, JOIN, GROUP BY)
- [ ] Basic familiarity with Python

---

## Part 1: Local Setup (15 minutes)

### Step 1.1: Generate Sample Data

First, we'll create synthetic learning data on your local machine.

```bash
# Navigate to the databricks folder
cd databricks

# Generate sample data (creates ~180KB of parquet files)
python generate_synthetic_data.py
```

This creates realistic data in `data/`:
- 50 simulated students
- 500+ conversations
- 1000+ lesson progress records
- 200+ assessment attempts

**What's a Parquet file?** Parquet is a columnar storage format optimized for analytics. It's like a super-efficient CSV that compresses well and reads fast.

### Step 1.2: Verify the Data

```bash
# Check that files were created
ls -la data/
```

You should see 7 parquet files totaling about 180KB.

---

## Part 2: Databricks Account Setup (20 minutes)

### Step 2.1: Create a Free Databricks Account

1. Go to [databricks.com/try-databricks](https://www.databricks.com/try-databricks)
2. Click **"Try Databricks Free"**
3. Choose **"Community Edition"** (free forever, no credit card)
4. Fill in your details and verify your email
5. You'll receive a workspace URL like `https://community.cloud.databricks.com/`

**What is a Databricks Workspace?** Think of it as your cloud-based development environment. It's where you'll write code, store data, and run analytics.

### Step 2.2: Start a Compute Cluster

A **cluster** is a set of cloud computers that run your code. For Community Edition, you get a small free cluster.

1. Log into your workspace
2. Click **"Compute"** in the left sidebar
3. Click **"Create Cluster"**
4. Keep the default settings (they're optimized for free tier)
5. Click **"Create Cluster"** and wait 3-5 minutes for it to start

The cluster shows **"Running"** (green dot) when ready.

**Why do I need a cluster?** Databricks uses Apache Spark to process data. Spark runs on clusters to handle large datasets. Even for small data, you need a cluster to execute code.

### Step 2.3: Upload the Notebooks

1. Click **"Workspace"** in the left sidebar
2. Right-click your username folder > **"Create"** > **"Folder"**
3. Name it `babblr-tutorial`
4. Right-click the new folder > **"Import"**
5. Upload all `.ipynb` files from `databricks/notebooks/`:
   - `01_bronze_layer.ipynb`
   - `02_silver_layer.ipynb`
   - `03_gold_layer.ipynb`
   - `04_dashboard.ipynb`

### Step 2.4: Upload the Data Files

For Community Edition, use **Volumes** (recommended):

1. Click **"Catalog"** in the left sidebar
2. Click **"+"** > **"Add"** > **"Add a volume"**
3. Create a volume with:
   - Catalog: `hive_metastore` (or your default)
   - Schema: Create new schema named `babblr`
   - Volume name: `bronze`
4. Click into the volume and use **"Upload"** to add all `.parquet` files from `data/`

**Alternative:** If Volumes aren't available, see the [Troubleshooting](#troubleshooting) section.

---

## Part 3: Run the Tutorial Notebooks (60-90 minutes)

Open each notebook, attach it to your running cluster (dropdown at top), and run the cells in order.

### Notebook 1: Bronze Layer (Raw Data)

**File:** `01_bronze_layer.ipynb`

**What you'll learn:**
- Loading Parquet files into Delta Lake tables
- Schema inference
- Basic data verification

**Key concept:** The Bronze layer stores data exactly as received - no transformations. This preserves the original data for auditing and reprocessing.

### Notebook 2: Silver Layer (Cleaned Data)

**File:** `02_silver_layer.ipynb`

**What you'll learn:**
- Data cleaning and validation
- Parsing JSON columns
- Joining tables
- Window functions

**Key concept:** The Silver layer transforms raw data into a clean, validated format. Bad records are filtered, schemas are standardized, and tables are joined.

### Notebook 3: Gold Layer (Analytics)

**File:** `03_gold_layer.ipynb`

**What you'll learn:**
- Creating aggregated metrics
- Complex SQL analytics
- MLflow experiment tracking
- K-Means clustering

**Key concept:** The Gold layer contains business-ready aggregates optimized for dashboards and reports. This is where you calculate KPIs and train ML models.

### Notebook 4: Dashboard

**File:** `04_dashboard.ipynb`

**What you'll learn:**
- Creating visualizations
- Building a dashboard
- Presenting analytics to stakeholders

**Key concept:** Dashboards turn data into actionable insights. Learn to create charts, arrange them into dashboards, and interpret the results.

---

## Understanding the Medallion Architecture

The **medallion architecture** is a data organization pattern used throughout industry:

```
+-------------------+
|   Source Data     |  (Parquet files, APIs, databases)
+---------+---------+
          |
          v
+---------+---------+
|   BRONZE LAYER    |  Raw data, no transformations
|   (01_bronze)     |  "Store everything exactly as received"
+---------+---------+
          |
          v
+---------+---------+
|   SILVER LAYER    |  Cleaned, validated, joined
|   (02_silver)     |  "Make it trustworthy"
+---------+---------+
          |
          v
+---------+---------+
|   GOLD LAYER      |  Aggregated, business-ready
|   (03_gold)       |  "Make it useful"
+---------+---------+
          |
          v
+---------+---------+
|   DASHBOARDS      |  Visualizations, reports
|   (04_dashboard)  |  "Make it actionable"
+---------+---------+
```

**Real-world analogy:** Think of it like cooking:
- **Bronze** = Raw ingredients from the grocery store
- **Silver** = Prepped ingredients (washed, cut, measured)
- **Gold** = Finished dishes ready to serve

**Is this Databricks-specific?** No! The medallion pattern works with any data platform (Snowflake, BigQuery, etc.). Databricks just makes it easy with Delta Lake.

---

## Data Model

The tutorial uses learning data from the Babblr language learning app:

```
+-------------------+       +-------------------+
|   Conversations   | ----> |     Messages      |
|   - language      |       |   - content       |
|   - cefr_level    |       |   - corrections   |
+-------------------+       +-------------------+

+-------------------+       +-------------------+
|     Lessons       | ----> |  LessonProgress   |
|   - lesson_type   |       |   - mastery_score |
|   - subject       |       |   - status        |
+-------------------+       +-------------------+

+-------------------+       +-------------------+
|   Assessments     | ----> | AssessmentAttempt |
|   - type          |       |   - score         |
|   - difficulty    |       |   - skill_scores  |
+-------------------+       +-------------------+

+-------------------+
|    UserLevels     |
|   - cefr_level    |
|   - proficiency   |
+-------------------+
```

---

## Key Analytics Questions

The tutorial helps answer these business questions:

1. **Learning Velocity**: How fast do students progress through CEFR levels?
2. **Lesson Effectiveness**: Which lessons correlate with highest assessment gains?
3. **Topic Engagement**: What topics keep students most engaged?
4. **Student Segments**: Can we cluster students by their learning patterns?
5. **At-Risk Detection**: Which students are likely to drop off?

---

## Troubleshooting

### "Public DBFS root is disabled" Error

Community Edition restricts some storage paths. Solutions:

1. **Use Volumes** (recommended) - see Step 2.4 above
2. **Use /tmp/** - Upload to `/tmp/babblr/bronze/` and update the notebook path
3. **Use notebook upload** - Click the paperclip icon in the notebook to upload files

### Cluster Won't Start

- Community Edition clusters auto-terminate after 2 hours of inactivity
- Click "Start" to restart a terminated cluster
- If it fails, try creating a new cluster

### Data Generation Produces Same Data

This is expected! The script uses a fixed seed for reproducibility. To generate different data:

```bash
python generate_synthetic_data.py --seed 123
```

---

## Folder Structure

```
databricks/
+-- README.md                    # This file
+-- export_data.py               # Export from real Babblr SQLite (optional)
+-- generate_synthetic_data.py   # Generate sample data for tutorial
+-- data/                        # Generated Parquet files (not in git)
|   +-- conversations.parquet
|   +-- messages.parquet
|   +-- lessons.parquet
|   +-- lesson_progress.parquet
|   +-- assessments.parquet
|   +-- assessment_attempts.parquet
|   +-- user_levels.parquet
+-- notebooks/
    +-- 01_bronze_layer.ipynb    # Raw data ingestion
    +-- 02_silver_layer.ipynb    # Data cleaning & joins
    +-- 03_gold_layer.ipynb      # Analytics & MLflow
    +-- 04_dashboard.ipynb       # Visualizations
```

---

## Next Steps

After completing the tutorial, try these extensions:

- [ ] Add real-time streaming with Structured Streaming
- [ ] Build an A/B testing framework for lesson experiments
- [ ] Create a recommendation engine for personalized learning paths
- [ ] Implement cohort analysis with retention curves
- [ ] Explore Unity Catalog for data governance
- [ ] Set up Delta Live Tables for automated pipelines

---

## Interview Talking Points

When presenting this project:

1. **Medallion Architecture**: "I structured the data lake using Bronze/Silver/Gold layers for clear separation of raw, cleaned, and business-ready data."

2. **Delta Lake Benefits**: "Delta Lake gives us ACID transactions, time travel, and schema evolution - critical for a production analytics platform."

3. **MLflow Integration**: "I used MLflow to track experiments when clustering students by error patterns, ensuring reproducibility."

4. **Dashboard Design**: "The dashboard focuses on actionable metrics: which lessons work, which students need intervention, and how to optimize the curriculum."
