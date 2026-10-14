# Process Walkthrough: Step by Step

This document explains, in order, every step taken in this project, from the business question through to the recommendations. For each step it covers **what was done**, **where it is in the code**, and **why it was done that way**. It also gives the exact commands to reproduce each step.

The project follows the six-phase **Ask → Prepare → Process → Analyze → Share → Act** framework. The steps below are grouped by phase.

| Phase | Steps | Main files |
|---|---|---|
| Setup | 0 | `requirements.txt`, `pyproject.toml` |
| Ask | 1 | `docs/CASESTUDY.md` |
| Prepare | 2–3 | `src/bellabeat/config.py`, `src/bellabeat/data_loading.py` |
| Process | 4–5 | `src/bellabeat/cleaning.py`, `src/bellabeat/transform.py` |
| Analyze | 6–7 | `src/bellabeat/analysis.py`, `src/bellabeat/segmentation.py` |
| Share | 8 | `src/bellabeat/visualization.py`, `docs/*.md` |
| Validate | 9–10 | `sql/*.sql`, `scripts/build_sqlite_db.py`, `scripts/run_sql_analysis.py`, `tests/` |
| Act | 11 | `docs/insights_and_recommendations.md` |

---

## Step 0: Set up the environment

1. Install Python 3.11 or newer (the project was developed on 3.12).
2. From the project root, create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
   .\.venv\Scripts\Activate.ps1
   ```

   On macOS or Linux, use `python3 -m venv .venv` and `source .venv/bin/activate` instead.
3. Install the pinned dependencies:

   ```bash
   pip install -r requirements.txt
   ```

The package itself does not need to be installed. Each script adds `src/` to `sys.path`.

---

## Phase 1: Ask

### Step 1: Define the business task

1. Read the brief in `docs/CASESTUDY.md`.
2. Identify the stakeholders: Urška Sršen (Co-founder and Chief Creative Officer), Sando Mur (Co-founder and Mathematician), and the Bellabeat marketing analytics team.
3. Write down the three guiding questions:
   - How do users use their smart devices?
   - How could these trends apply to Bellabeat customers?
   - How could these trends help influence Bellabeat's marketing strategy?
4. Restate them as one business task: *analyze how consumers use non-Bellabeat smart devices, and turn the usage patterns into marketing recommendations for one Bellabeat product.*

Every later analysis step answers one of these three questions. Each chart title is phrased as a business question for the same reason.

---

## Phase 2: Prepare

### Step 2: Acquire and inspect the data

1. Download the *Fitbit Fitness Tracker Data* (Furberg et al., Zenodo record 53894, also on Kaggle).
2. Extract it under `data/`. It contains two Fitabase export folders:
   - `mturkfitbit_export_3.12.16-4.11.16` (35 users)
   - `mturkfitbit_export_4.12.16-5.12.16` (33 users)
3. Treat the raw CSVs as **read-only**. No step in this project writes to `data/`.
4. List the files in each export and compare their columns, row counts, user IDs, and date ranges.

### Step 3: Select the data source and centralize configuration

**Decision:** use only the April–May export (`4.12.16-5.12.16`).

**Why:**
- Only that export has `sleepDay_merged.csv` and the daily-aggregate files. Every sleep question depends on them.
- The two exports overlap on 2016-04-12 and have different user rosters, so merging them would double-count user-days.
- It is a complete 31-day period, so "days used out of 31" is a well-defined device-usage metric.

**How it was implemented:**
1. All paths and thresholds are defined once, in `src/bellabeat/config.py`:
   - `PRIMARY_EXPORT_DIR` / `EXCLUDED_EXPORT_DIR`: the export decision.
   - `RAW_FILES`: a dictionary mapping each table name to its CSV path.
   - Thresholds such as `MINUTES_PER_DAY`, `STEP_TIER_BINS`, plausibility bounds, `STUDY_PERIOD_DAYS`, and `RANDOM_SEED = 42`.
2. Loaders in `src/bellabeat/data_loading.py` read each CSV and **only** parse the date columns. They do no cleaning, so the data-quality checks see the data exactly as shipped.
   - `ActivityDate` is parsed as `%m/%d/%Y`.
   - `SleepDay`, `ActivityHour`, and `Date` are parsed as `%m/%d/%Y %I:%M:%S %p`.
   - A missing file raises `FileNotFoundError` with the expected path.
3. `load_all_core()` loads the six tables the analysis needs: daily activity, sleep, hourly steps, hourly calories, hourly intensities, and weight log. The heart-rate file (about 2.5 million rows) is left out to keep the pipeline fast.

---

## Phase 3: Process

### Step 4: Clean each table

**Principle:** never drop data silently. Each function in `src/bellabeat/cleaning.py` returns `(clean_df, report_dict)`, and every removed or flagged row is counted in the report.

#### 4a. Daily activity (`clean_daily_activity`)

1. Drop exact duplicate rows. *(0 found)*
2. Drop duplicate `(Id, ActivityDate)` keys. *(0 found)*
3. Count steps above 50,000 and calories outside 500–6,000. These are reported, not dropped. *(5 low-calorie rows, consistent with partial-wear days)*
4. Drop rows with negative steps, calories, or minutes. *(0 found)*
5. **Flag non-wear days.** A day with `TotalSteps = 0` and `SedentaryMinutes = 1440` is marked `is_non_wear_day = True`. *(72 rows)* These rows are **kept**: they are excluded from activity averages but still counted when measuring how often the device is worn.
6. Count days where logged minutes exceed 1,440. *(0 found)*

Result: 940 rows in, 940 rows out, 33 users, 2016-04-12 to 2016-05-12.

#### 4b. Sleep (`clean_sleep_day`)

1. Drop exact duplicates. *(3 found)*
2. Drop sleep durations outside 30–900 minutes. *(0 found)*
3. Drop rows where time in bed is less than time asleep. *(0 found)*
4. Group by `(Id, SleepDay)` and sum. This is a safeguard in case a future export has multiple rows per day; on this export it changes nothing.

Result: 413 rows in, 410 rows out, 24 users.

#### 4c. Weight log (`clean_weight_log`)

1. Drop exact duplicates. *(0 found)*
2. Report the share of missing `Fat` values (97%) and manual entries (61.2%). `Fat` is not imputed.

Result: 67 rows, 8 users. This is too sparse for analysis, so weight is reported but not analyzed.

#### 4d. Hourly tables (`clean_hourly`)

The same function runs on steps, calories, and intensities:

1. Drop exact duplicates and duplicate `(Id, ActivityHour)` keys.
2. Drop negative values.

Result: 22,099 rows each, 0 removed, 33 users.

All six reports are saved to `outputs/tables/data_quality_reports.json`. The written explanation is in `docs/data_quality_report.md`.

### Step 5: Transform into analysis-ready tables

Functions in `src/bellabeat/transform.py`:

1. **Add derived activity fields** (`add_activity_derived_fields`):
   - `total_active_minutes` = very + fairly + lightly active minutes
   - `total_logged_minutes` = active + sedentary minutes
   - `sedentary_share_pct` = sedentary minutes as a percentage of logged minutes
   - `activity_tier`: steps binned into the five Tudor-Locke & Bassett (2004) bands (Sedentary < 5,000; Low active 5,000–7,499; Somewhat active 7,500–9,999; Active 10,000–12,499; Highly active 12,500+)
2. **Build the user-day master** (`build_user_day_master`):
   - **Left join** sleep onto activity on `(Id, date)`, validated as one-to-one.
   - Add `has_sleep_log`, `day_of_week`, `is_weekend`, and `week_number`.
   - *Why a left join:* only 24 of 33 users logged sleep. An inner join would remove 9 users from every activity question.
3. **Build the user summary** (`build_user_summary`), one row per user:
   - `device_usage_days` and `device_usage_rate_pct` use **all** days, including non-wear days.
   - Activity averages (steps, calories, sedentary and active minutes, distance) use **worn days only**.
   - Sleep averages use **logged nights only**.
   - Each user gets an `activity_tier` based on their average daily steps.
4. **Build hourly usage** (`build_hourly_usage`):
   - Inner join the three hourly tables on `(Id, ActivityHour)`.
   - Add `hour_of_day`, `day_of_week`, `is_weekend`, and `date`.

The three tables are written to `data_processed/` (`user_day_master.csv`, `user_summary.csv`, `hourly_usage.csv`). They can be opened directly in Excel, Tableau, or Power BI.

---

## Phase 4: Analyze

### Step 6: Run descriptive and statistical analysis

All functions are in `src/bellabeat/analysis.py`. Activity questions use **worn days only** (`~is_non_wear_day`, n = 868).

1. **Descriptive statistics** (`describe_numeric`). For steps, calories, sedentary minutes, active minutes, distance, and sleep, compute n, mean, median, SD, min, P25, P75, max, and the mean-vs-median skew %. Mean and median are both reported because tracker data is right-skewed.
2. **Correlation tests** (`correlation_test`). Pearson r, two-sided, with p-value and r²:
   - Steps vs. calories (worn days)
   - Distance vs. calories (worn days)
   - Steps vs. sleep minutes (worn days with a sleep log, n = 410)
   - Sedentary minutes vs. sleep minutes (same population). This produced the key finding: r = −0.601.
3. **Weekday vs. weekend tests** (`weekday_weekend_test`). Welch's t-test (no equal-variance assumption) on steps and on sedentary minutes. Steps showed no significant difference (p = 0.871).
4. **Activity tier distribution** (`activity_tier_distribution`). Computed twice: once per worn day and once per user. The two answer different questions.
5. **Device-usage frequency** (`device_usage_frequency`). Users are bucketed by days logged: ≤10, 11–20, 21–27, 28–31.
6. **Time-of-day and day-of-week profiles** (`hourly_activity_profile`, `weekday_activity_profile`). Average steps and calories by hour (split weekday/weekend) and by day of week.

Every test records its hypothesis, method, n, statistic, p-value, and significance at α = 0.05 in `outputs/tables/statistical_test_results.json`. All results are reported as associations, not causes.

### Step 7: Segment users

In `src/bellabeat/segmentation.py`:

1. Select four per-user features: `avg_daily_steps`, `avg_sedentary_minutes`, `avg_active_minutes`, and `avg_daily_calories`. Users missing any feature are excluded and counted (0 on this data).
2. Standardize the features with `StandardScaler`.
3. Fit k-means for k = 2, 3, and 4 (`n_init=10`, `random_state=42`). k is capped at 4 because with 33 users, more clusters produce segments of 2–3 people.
4. Pick the k with the highest silhouette score. Scores were 0.342 (k = 2), 0.331 (k = 3), and 0.339 (k = 4), so **k = 2** was chosen.
5. Sort clusters by average steps and give them stable names, because k-means cluster numbers are arbitrary:
   - **Low activity:** 12 users, about 4,819 steps/day, about 1,140 sedentary min/day
   - **High activity:** 21 users, about 9,639 steps/day, about 872 sedentary min/day
6. Save `outputs/tables/user_segments.csv` and `outputs/tables/segmentation_report.json`.

A silhouette score around 0.34 means the separation is real but moderate. The segments are useful for messaging, not for strict classification.

---

## Phase 5: Share

### Step 8: Visualize and write up

1. `src/bellabeat/visualization.py` produces ten charts in `outputs/figures/` at 150 dpi, using the headless `Agg` backend. Each chart title is phrased as the business question it answers. The full list is in README Section 10.
2. The written deliverables, in reading order:
   1. `docs/executive_summary.md`: the answer on one page
   2. `docs/insights_and_recommendations.md`: five recommendations with evidence
   3. `docs/analysis_findings.md`: full statistics and segmentation
   4. `docs/data_quality_report.md`: data selection, cleaning, and limitations

`docs/data_quality_report.md` was written from `data_quality_reports.json`. The pipeline does not regenerate it, so update it by hand if the cleaning rules change.

### Running Steps 2–8 in one command

```bash
python scripts/run_pipeline.py
```

`scripts/run_pipeline.py` runs, in order: load → clean (collecting reports) → transform → write `data_processed/` → descriptive stats → correlations → t-tests → tiers and profiles → segmentation → ten charts → quality-report JSON. Every run overwrites the previous outputs and produces identical results, because k-means is seeded.

---

## Validation

### Step 9: Re-implement the analysis in SQL and cross-check

The same logic was written a second time in SQLite to check the Python results and to serve SQL/BI users.

1. **Load the raw CSVs into SQLite:**

   ```bash
   python scripts/build_sqlite_db.py
   ```

   This deletes and rebuilds `data_processed/bellabeat.db`, creates six `raw_*` tables, and converts all dates to ISO 8601 text so SQLite's date functions work on them.
2. **Apply the views and run the queries:**

   ```bash
   python scripts/run_sql_analysis.py
   ```

   This runs, in order:
   1. `sql/cleaning_views.sql`: `clean_daily_activity`, `clean_sleep_day`, `clean_weight_log`, and the three `clean_hourly_*` views. These mirror `cleaning.py`.
   2. `sql/transform_views.sql`: `activity_with_derived_fields`, `user_day_master`, `user_summary`, and `hourly_usage`. These mirror `transform.py`.
   3. The four analysis files: `descriptive_stats.sql`, `correlation_analysis.sql`, `weekday_weekend_and_hourly.sql`, and `device_usage_and_segments.sql`.

   Each query result is saved as `outputs/tables/sql_version/<file>_<NN>.csv`.
3. **Compare** `outputs/tables/sql_version/*.csv` with the Python outputs in `outputs/tables/`. They agree on all counts, means, and Pearson r (to three decimals). The three intentional differences are:
   - **Percentiles:** SQL uses nearest-rank, because SQLite has no `PERCENTILE_CONT`.
   - **Correlation significance:** SQL reports the t-statistic only, with no p-value.
   - **Segmentation:** SQL uses a median split on average steps instead of k-means.

   The Python results are authoritative.

For interactive use, open `sqlite3 data_processed/bellabeat.db` and `.read` the files in the same order: cleaning views, then transform views, then any analysis file. `sql/schema.sql` is reference only.

### Step 10: Unit-test the logic

```bash
python -m pytest
```

There are 23 tests in four modules (`test_cleaning.py`, `test_transform.py`, `test_analysis.py`, `test_segmentation.py`). They run on small synthetic fixtures in `tests/conftest.py`, not on the real data, so each expected value can be checked by hand. They cover duplicate removal, non-wear flagging, sleep aggregation, the left-join behavior, the user summary, statistical outputs, tier bucketing, and segment labeling.

---

## Phase 6: Act

### Step 11: Turn findings into recommendations

Each finding was mapped to one marketing action. The full reasoning is in `docs/insights_and_recommendations.md`.

| Finding | Recommendation |
|---|---|
| Sedentary time is associated with less sleep (r = −0.601). Steps barely are (r = −0.190). | Market movement reminders as a sleep-quality feature. |
| The median worn day is 66% sedentary. | Lead content with "sit less" instead of "walk more." |
| 82% of users logged activity on 28+ days, but only 73% ever logged sleep. | Run a dedicated sleep-logging engagement campaign. |
| Weekday and weekend totals are the same, but the timing of peaks differs. | Time notifications to when users are actually active. |
| Users split into Low (36%) and High (64%) activity segments. | Replace the universal step goal with a personalized one. |

Every recommendation is treated as a **hypothesis to test against Bellabeat's own customer data**. The sample is 33 self-selected users from 2016, with no demographic information (see README Section 13).

---

## Quick reference: full reproduction

```bash
# 0. Setup (once)
python -m venv .venv
.\.venv\Scripts\Activate.ps1            # or: source .venv/bin/activate
pip install -r requirements.txt

# Steps 2-8: Python pipeline
python scripts/run_pipeline.py

# Step 9: SQL version and cross-check
python scripts/build_sqlite_db.py
python scripts/run_sql_analysis.py

# Step 10: tests
python -m pytest
```
