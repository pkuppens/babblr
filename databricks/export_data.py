#!/usr/bin/env python3
"""
Export Babblr SQLite database to Parquet files for Databricks import.

Usage:
    python export_data.py [--db-path PATH] [--output-dir DIR]

Example:
    python export_data.py --db-path ../backend/babblr.db --output-dir ./data
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


TABLES = [
    "conversations",
    "messages",
    "lessons",
    "lesson_items",
    "lesson_progress",
    "grammar_rules",
    "assessments",
    "assessment_questions",
    "assessment_attempts",
    "user_levels",
]


def export_table(conn: sqlite3.Connection, table: str, output_dir: Path) -> int:
    """Export a single table to Parquet format."""
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        if len(df) == 0:
            print(f"  [SKIP] {table}: empty table")
            return 0

        output_path = output_dir / f"{table}.parquet"
        df.to_parquet(output_path, index=False)
        print(f"  [OK] {table}: {len(df)} rows -> {output_path.name}")
        return len(df)
    except Exception as e:
        print(f"  [ERROR] {table}: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Export Babblr SQLite to Parquet")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("../backend/babblr.db"),
        help="Path to SQLite database",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./data"),
        help="Output directory for Parquet files",
    )
    args = parser.parse_args()

    # Validate database exists
    if not args.db_path.exists():
        print(f"[ERROR] Database not found: {args.db_path}")
        print("[INFO] Use generate_synthetic_data.py to create sample data instead")
        return 1

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Exporting from: {args.db_path}")
    print(f"[INFO] Output directory: {args.output_dir}")
    print()

    # Connect and export
    conn = sqlite3.Connection(args.db_path)
    total_rows = 0

    for table in TABLES:
        total_rows += export_table(conn, table, args.output_dir)

    conn.close()

    print()
    print(f"[DONE] Exported {total_rows} total rows to {args.output_dir}")
    print()
    print("Next steps:")
    print("  1. Upload Parquet files to Databricks DBFS:")
    print("     /FileStore/babblr/bronze/")
    print("  2. Run notebook 01_bronze_layer.py to create Delta tables")

    return 0


if __name__ == "__main__":
    exit(main())
