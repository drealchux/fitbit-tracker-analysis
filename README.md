# Bellabeat Smart Device Usage Analysis

A business intelligence analysis of the Fitbit Fitness Tracker dataset (Fitabase, 33 users, 31 days) for Bellabeat, following the Ask -> Prepare -> Process -> Analyze -> Share -> Act workflow. Implemented twice, independently: once in Python (pandas), once in SQL (SQLite), with results cross-checked against each other.

**Start here if you want the findings, not the code:** `docs/executive_summary.md`.

## Project layout

```
data/                       Raw Fitabase CSV exports (not modified by this project)
data_processed/             Analysis-ready output: user_day_master.csv, user_summary.csv,
                             hourly_usage.csv, bellabeat.db (SQLite)
docs/
  CASESTUDY.md               Original case study brief (Ask/Prepare framing)
  data_quality_report.md     Prepare/Process phase: what was cleaned, why, and how
  analysis_findings.md       Analyze phase: descriptive stats, statistical tests, segmentation
  insights_and_recommendations.md   Act phase: 5 evidence-based recommendations
  executive_summary.md       One-page business summary
outputs/
  figures/                    9 charts (PNG), each answering one business question
  tables/                     Descriptive stats, test results, segments, device usage (CSV/JSON)
  tables/sql_version/         Same analyses, produced by the SQL implementation
src/bellabeat/               Python package: config, data_loading, cleaning, transform,
                              analysis, segmentation, visualization
sql/                          SQL implementation: schema, cleaning views, transform views,
                               descriptive stats, correlation, weekday/hourly, segmentation
scripts/
  run_pipeline.py             Runs the full Python pipeline end to end
  build_sqlite_db.py          Loads the raw CSVs into data_processed/bellabeat.db
  run_sql_analysis.py         Runs the SQL analysis and saves results to outputs/tables/sql_version/
tests/                        pytest unit tests for cleaning, transform, analysis, segmentation
```

## Setup

Requires Python 3.11+. From the project root:

**PowerShell**
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**bash / Git Bash**
```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows Git Bash
# source .venv/bin/activate      # macOS / Linux
pip install -r requirements.txt
```

## Running the Python analysis

```bash
python scripts/run_pipeline.py
```

This loads the raw CSVs, cleans and transforms them, runs the descriptive and statistical analysis, clusters users into behavioral segments, generates all 9 charts, and writes every intermediate result to `data_processed/` and `outputs/`. Re-running it is safe and deterministic (segmentation is seeded; see `config.RANDOM_SEED`).

Run the tests with:
```bash
python -m pytest
```

## Running the SQL analysis

The SQL version is a second, independent implementation of the same cleaning and analysis logic, for readers or teams who work primarily in SQL/BI tools rather than Python.

```bash
python scripts/build_sqlite_db.py   # loads the raw CSVs into data_processed/bellabeat.db
python scripts/run_sql_analysis.py  # applies sql/*.sql and saves results to outputs/tables/sql_version/
```

Or, to explore interactively with the `sqlite3` CLI or any SQLite client (e.g. DB Browser for SQLite):
```bash
sqlite3 data_processed/bellabeat.db
sqlite> .read sql/cleaning_views.sql
sqlite> .read sql/transform_views.sql
sqlite> .read sql/descriptive_stats.sql
```

See `sql/schema.sql` for the raw table structure and `docs/data_quality_report.md` (Section 5) for the two documented, minor numerical differences between the Python and SQL implementations (percentile method; segmentation method).

## Why one export folder, not both

The dataset ships as two overlapping Fitabase exports with different user rosters; only one (`mturkfitbit_export_4.12.16-5.12.16`) has the daily sleep and daily-aggregate files this analysis depends on. The full reasoning is in `docs/data_quality_report.md`, Section 1.

## Reading order

1. `docs/executive_summary.md` — the answer, in one page.
2. `docs/insights_and_recommendations.md` — the 5 recommendations, each tied to a specific finding.
3. `docs/analysis_findings.md` — the full analysis behind those findings.
4. `docs/data_quality_report.md` — what the data looked like, what was cleaned, and what its limitations are.
5. `outputs/figures/` — the supporting charts, referenced throughout the docs above.
