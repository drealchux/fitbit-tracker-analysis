# Data Quality Report

**Phases covered:** Prepare, Process
**Source:** Fitabase Fitbit Fitness Tracker Data (Furberg, Brinton, Keating, Ortiz; distributed via Kaggle, originally from Zenodo record 53894)
**Pipeline that produced this report:** `scripts/run_pipeline.py`, backed by `src/bellabeat/cleaning.py`. Every number below is read directly from `outputs/tables/data_quality_reports.json`, which the pipeline regenerates on every run.

---

## 1. Which data was used, and why

The dataset ships as two Fitabase export folders:

| Export folder | Date range | Users | Has daily-aggregate files (dailyCalories, dailySteps, dailyIntensities, sleepDay)? |
|---|---|---|---|
| `mturkfitbit_export_4.12.16-5.12.16` | 2016-04-12 to 2016-05-12 (31 days) | 33 | Yes |
| `mturkfitbit_export_3.12.16-4.11.16` | 2016-03-12 to 2016-04-12 (31 days) | 35 | No |

This analysis uses **only the 4/12-5/12/2016 export**. Three reasons:

1. It is the only export with `sleepDay_merged.csv`, which every sleep-related business question in this brief depends on.
2. The two exports overlap on 2016-04-12 and have different, non-identical user rosters (33 vs. 35 IDs), so combining them would risk double-counting some user-days and would still leave the earlier period without sleep data.
3. It is a complete, self-contained 31-day period, which keeps "days used out of the study period" (a device-usage metric requested in the brief) well-defined.

The excluded export is not deleted; it remains under `data/` and is simply not read by the pipeline. This decision is encoded in `src/bellabeat/config.py` as `PRIMARY_EXPORT_DIR` / `EXCLUDED_EXPORT_DIR`.

## 2. Dataset overview (primary export)

| Table | Rows | Unique users | Date range |
|---|---:|---:|---|
| Daily activity | 940 | 33 | 2016-04-12 to 2016-05-12 |
| Sleep (post-cleaning) | 410 | 24 | 2016-04-12 to 2016-05-12 |
| Hourly steps / calories / intensities | 22,099 each | 33 | 2016-04-12 to 2016-05-12 |
| Weight log | 67 | 8 | 2016-04-12 to 2016-05-12 |
| Heart rate (second-level) | 2,483,658 | 14 | 2016-04-12 to 2016-05-12 |

**Sample size limitation, stated explicitly:** this is 33 people who opted into an Amazon Mechanical Turk survey in early 2016 and agreed to share Fitbit data. Age, gender, health status, and geography are not recorded anywhere in the export. Bellabeat's customer base is women; this dataset's gender composition is unknown and cannot be assumed to match. Every finding in this project describes **these 33 users during this 31-day window**, not smart-device users in general. Findings should inform hypotheses to test against Bellabeat's own user data, not be treated as conclusions about Bellabeat customers.

Coverage is also uneven across tables: 33 of 33 users have daily activity, but only 24 (72.7%) ever logged sleep, and only 8 (24.2%) ever logged weight. Weight-based analysis was excluded from this project for that reason; it would describe 8 people, not 33.

## 3. Cleaning steps and findings, per table

### 3.1 Daily activity (`dailyActivity_merged.csv`)

| Check | Result |
|---|---:|
| Exact duplicate rows | 0 dropped |
| Duplicate (Id, ActivityDate) rows | 0 dropped |
| Rows with steps > 50,000 (implausible) | 0 |
| Rows with calories outside 500-6,000 (implausible) | 5 |
| Rows with negative values | 0 |
| Rows flagged as non-wear days | 72 (7.7% of rows) |
| Rows with logged minutes > 1,440/day | 0 |

- **Non-wear days**: a row with `TotalSteps = 0` and `SedentaryMinutes = 1440` records a device that logged the full day as sedentary with zero steps, which is far more consistent with the device sitting on a table than with 24 hours of continuous stillness. These 72 rows (from 15 of the 33 users) are kept in the data and flagged with `is_non_wear_day`, not deleted, because deleting them would erase evidence of how often devices go unworn, which is itself one of the business questions. They are excluded only from activity-level averages (steps, calories, active minutes), not from device-usage-frequency counts.
- **Implausible-calorie rows**: 5 rows (0.5% of the table) have calorie totals under 500, each paired with under two hours of logged minutes for that day (for example, one row logs only 2 total minutes across all activity levels). These read as partial-day device removal, not full non-wear days, so the `TotalSteps = 0 AND SedentaryMinutes = 1440` rule does not catch them. They are flagged in the quality report and left in the data; at 5 of 940 rows they do not materially affect any reported average.

### 3.2 Sleep (`sleepDay_merged.csv`)

| Check | Result |
|---|---:|
| Exact duplicate rows | 3 dropped |
| Rows with sleep duration outside 30-900 minutes | 0 |
| Rows where time-in-bed < time-asleep | 0 |
| Rows with more than one session already rolled in (`TotalSleepRecords` > 1) | 46 |
| Rows after cleaning | 410 (one row per user-day) |

- 3 rows were byte-for-byte duplicates of another row (same user, same day, same values) and were dropped.
- The table already ships as one row per (user, day); `TotalSleepRecords` indicates how many sleep sessions (e.g., a nap plus an overnight sleep) were summed into that row by Fitabase. A defensive `GROUP BY (Id, SleepDay)` aggregation step runs after deduplication in case a future export ever splits sessions into separate rows; on this export it is a no-op beyond removing the 3 exact duplicates.

### 3.3 Weight log (`weightLogInfo_merged.csv`)

| Check | Result |
|---|---:|
| Exact duplicate rows | 0 dropped |
| Missing `Fat` values | 97.0% |
| Manually entered rows (`IsManualReport`) | 61.2% |

Body fat percentage is missing for all but 2 of 67 rows because it requires a body-fat scale most users evidently did not have; it is excluded from analysis rather than imputed. Weight itself (`WeightKg`) is complete but covers only 8 users and is not used in the core analysis for that reason (see Section 2).

### 3.4 Hourly steps, calories, intensities

| Check | hourly_steps | hourly_calories | hourly_intensities |
|---|---:|---:|---:|
| Exact duplicate rows | 0 | 0 | 0 |
| Duplicate (Id, hour) rows | 0 | 0 | 0 |
| Negative values | 0 | 0 | 0 |

All three hourly tables were clean on every check performed; they are used as-is after the standard duplicate/negative-value checks.

## 4. Transformations applied

| Step | What it does | Where |
|---|---|---|
| Non-wear flagging | Adds `is_non_wear_day` to daily activity | `cleaning.clean_daily_activity` |
| Derived activity fields | Adds `total_active_minutes`, `sedentary_share_pct`, `activity_tier` | `transform.add_activity_derived_fields` |
| User-day master join | Left-joins sleep onto activity by (Id, date) | `transform.build_user_day_master` |
| Calendar fields | Adds day-of-week name and weekend flag | `transform.add_calendar_fields` |
| Per-user summary | One row per user: usage days, activity averages (worn days only), sleep averages (logged nights only) | `transform.build_user_summary` |
| Hourly usage merge | Joins hourly steps/calories/intensities, adds hour-of-day and weekday fields | `transform.build_hourly_usage` |

The activity-sleep join is a **left join on activity**, not an inner join, and this is a deliberate choice: activity is logged by all 33 users, sleep by only 24. An inner join would silently drop 9 users (27%) from every question about steps, calories, or sedentary time, even though those questions do not require a sleep record. Rows without a matching sleep entry simply carry `has_sleep_log = 0` and null sleep columns; they are excluded only from sleep-specific calculations.

## 5. Method note: Python vs. SQL implementations

Both a Python (pandas) and a SQL (SQLite) implementation of this cleaning and analysis exist, under `src/bellabeat/` and `sql/` respectively. They were cross-checked against each other (`scripts/run_sql_analysis.py` output vs. `scripts/run_pipeline.py` output) and agree on every count and mean reported above, and on Pearson correlation coefficients to 3 decimal places. Two documented differences exist:

1. **Percentiles**: the Python version uses pandas' linear-interpolation percentile; the SQL version uses the nearest-rank method (SQLite has no built-in `PERCENTILE_CONT`). Values are close but not identical (for example, p25 daily steps: 4,824.8 in Python vs. 4,832.0 in SQL).
2. **Segmentation**: the Python version uses k-means clustering on four standardized features (see `docs/analysis_findings.md`, Section 4). Replicating k-means in standard SQL is impractical, so the SQL version (`sql/device_usage_and_segments.sql`) instead splits users at the median of average daily steps, a simpler one-dimensional rule any BI tool can reproduce. The Python k-means result is the authoritative segmentation used in this project's recommendations; the SQL version is provided for teams working purely in SQL/BI tooling who need a directional answer.

## 6. Summary of limitations carried into the analysis

- 33 users, self-selected into an MTurk survey, over 31 days: too small and unvetted to generalize to Bellabeat's customer base statistically.
- Demographic composition (gender, age, health status) is unknown, which matters specifically because Bellabeat's product line targets women.
- Sleep data covers 24 of 33 users; weight data covers 8 of 33 and was excluded from the core analysis.
- Heart rate data covers 14 of 33 users and is summarized only as a coverage statistic (Section 2), not used in the behavioral analysis, since fewer than half of users have it.
- All data is from April-May 2016. Fitbit hardware, app design, and user behavior have changed substantially since; findings describe a historical dataset, not current smart-device usage.
