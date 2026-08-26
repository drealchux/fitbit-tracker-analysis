"""Execute the sql/ scripts against data_processed/bellabeat.db and save
every query result to outputs/tables/sql_version/, so the SQL analysis
produces the same kind of inspectable output tables as the Python
pipeline.

This also acts as a parity check: comparing outputs/tables/sql_version/*.csv
against the Python pipeline's outputs/tables/*.csv is how the two
independent implementations are cross-validated against each other.

Usage (from the project root, with the virtual environment active; run
scripts/build_sqlite_db.py first if data_processed/bellabeat.db does not
exist yet):
    python scripts/run_sql_analysis.py
"""

from __future__ import annotations
import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
from bellabeat import config

DB_PATH = config.PROJECT_ROOT / "data_processed" / "bellabeat.db"
SQL_DIR = config.PROJECT_ROOT / "sql"
OUT_DIR = config.TABLES_DIR / "sql_version"

VIEW_FILES = ["cleaning_views.sql", "transform_views.sql"]
QUERY_FILES = [
    "descriptive_stats.sql",
    "correlation_analysis.sql",
    "weekday_weekend_and_hourly.sql",
    "device_usage_and_segments.sql",
]


def split_statements(sql_text: str) -> list[str]:
    """Split a .sql file into individually executable statements.

    Comment lines (starting with '--') are dropped before splitting on
    ';', since none of these files put semicolons inside string literals
    but their prose comments do contain sentence-ending semicolons that
    would otherwise be mistaken for statement terminators.
    """
    code_only = "\n".join(
        line for line in sql_text.splitlines() if not line.strip().startswith("--")
    )
    statements = [stmt.strip() + ";" for stmt in code_only.split(";") if stmt.strip()]
    return statements


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"{DB_PATH} not found. Run scripts/build_sqlite_db.py first."
        )
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    try:
        for filename in VIEW_FILES:
            path = SQL_DIR / filename
            conn.executescript(path.read_text())
            print(f"Applied views from {filename}")

        for filename in QUERY_FILES:
            path = SQL_DIR / filename
            statements = split_statements(path.read_text())
            for i, stmt in enumerate(statements, start=1):
                df = pd.read_sql_query(stmt, conn)
                out_name = f"{path.stem}_{i:02d}.csv"
                df.to_csv(OUT_DIR / out_name, index=False)
                print(f"  {filename} statement {i}: {len(df)} rows -> {out_name}")
    finally:
        conn.close()

    print(f"\nSQL analysis outputs written to {OUT_DIR}")


if __name__ == "__main__":
    main()
