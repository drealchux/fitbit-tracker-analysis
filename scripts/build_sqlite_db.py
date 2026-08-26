"""Load the raw Fitabase CSVs into a SQLite database.

This is the only Python involved in the SQL version of the analysis: SQL
itself has no standard way to ingest a CSV file, so this script does
exactly that and nothing else. All cleaning, transformation, and analysis
logic lives in the .sql files under sql/, run afterward with sqlite3.

Usage (from the project root, with the virtual environment active):
    python scripts/build_sqlite_db.py
"""

from __future__ import annotations
import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
from bellabeat import config

DB_PATH = config.PROJECT_ROOT / "data_processed" / "bellabeat.db"

# Table name -> (csv path, {date column: strptime format})
TABLES = {
    "raw_daily_activity": (config.RAW_FILES["daily_activity"], {"ActivityDate": "%m/%d/%Y"}),
    "raw_sleep_day": (config.RAW_FILES["sleep_day"], {"SleepDay": "%m/%d/%Y %I:%M:%S %p"}),
    "raw_hourly_steps": (config.RAW_FILES["hourly_steps"], {"ActivityHour": "%m/%d/%Y %I:%M:%S %p"}),
    "raw_hourly_calories": (config.RAW_FILES["hourly_calories"], {"ActivityHour": "%m/%d/%Y %I:%M:%S %p"}),
    "raw_hourly_intensities": (
        config.RAW_FILES["hourly_intensities"],
        {"ActivityHour": "%m/%d/%Y %I:%M:%S %p"},
    ),
    "raw_weight_log": (config.RAW_FILES["weight_log"], {"Date": "%m/%d/%Y %I:%M:%S %p"}),
}


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        for table_name, (csv_path, date_cols) in TABLES.items():
            df = pd.read_csv(csv_path)
            for col, fmt in date_cols.items():
                # Normalize to ISO 8601 text (YYYY-MM-DD HH:MM:SS) so SQLite's
                # date()/strftime() functions work directly on the column.
                df[col] = pd.to_datetime(df[col], format=fmt).dt.strftime("%Y-%m-%d %H:%M:%S")
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"Loaded {len(df):>7} rows into {table_name}")
        conn.commit()
    finally:
        conn.close()

    print(f"\nSQLite database written to {DB_PATH}")


if __name__ == "__main__":
    main()
