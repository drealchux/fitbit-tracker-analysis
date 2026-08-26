-- Cleaning views: SQL equivalent of src/bellabeat/cleaning.py.
--
-- Run after scripts/build_sqlite_db.py has created the raw_* tables.
-- Each view mirrors one clean_* function from the Python pipeline so the
-- two implementations can be checked against each other; see
-- scripts/run_sql_analysis.py for an automated parity check.
--
-- Run with:
--   sqlite3 data_processed/bellabeat.db < sql/cleaning_views.sql

DROP VIEW IF EXISTS clean_daily_activity;
DROP VIEW IF EXISTS clean_sleep_day;
DROP VIEW IF EXISTS clean_weight_log;
DROP VIEW IF EXISTS clean_hourly_steps;
DROP VIEW IF EXISTS clean_hourly_calories;
DROP VIEW IF EXISTS clean_hourly_intensities;

-- ---------------------------------------------------------------------
-- Daily activity: de-duplicate, drop negative-value rows, flag non-wear
-- days (0 steps and all 1440 minutes sedentary is almost certainly a
-- device not worn, not a real 24-hour sedentary day).
-- ---------------------------------------------------------------------
CREATE VIEW clean_daily_activity AS
WITH deduped AS (
    SELECT DISTINCT * FROM raw_daily_activity
),
ranked AS (
    -- No ORDER BY: after SELECT DISTINCT, any rows sharing the same
    -- (Id, ActivityDate) key must differ on some other column (otherwise
    -- they would already be identical and removed above), so there is no
    -- meaningful "first" row to prefer; input order is used as-is.
    SELECT
        d.*,
        ROW_NUMBER() OVER (PARTITION BY Id, ActivityDate) AS rn
    FROM deduped d
)
SELECT
    Id,
    ActivityDate,
    TotalSteps,
    TotalDistance,
    TrackerDistance,
    LoggedActivitiesDistance,
    VeryActiveDistance,
    ModeratelyActiveDistance,
    LightActiveDistance,
    SedentaryActiveDistance,
    VeryActiveMinutes,
    FairlyActiveMinutes,
    LightlyActiveMinutes,
    SedentaryMinutes,
    Calories,
    CASE WHEN TotalSteps = 0 AND SedentaryMinutes = 1440 THEN 1 ELSE 0 END AS is_non_wear_day
FROM ranked
WHERE rn = 1
  AND TotalSteps >= 0
  AND Calories >= 0
  AND SedentaryMinutes >= 0
  AND VeryActiveMinutes >= 0;

-- ---------------------------------------------------------------------
-- Sleep: de-duplicate, drop implausible sleep durations (<30 min or >900
-- min) and rows where time in bed is less than time asleep, then group by
-- (Id, SleepDay) as a defensive aggregation (a no-op on this export, see
-- docs/data_quality_report.md).
-- ---------------------------------------------------------------------
CREATE VIEW clean_sleep_day AS
WITH deduped AS (
    SELECT DISTINCT * FROM raw_sleep_day
),
filtered AS (
    SELECT *
    FROM deduped
    WHERE TotalMinutesAsleep BETWEEN 30 AND 900
      AND TotalTimeInBed >= TotalMinutesAsleep
)
SELECT
    Id,
    SleepDay,
    SUM(TotalSleepRecords) AS TotalSleepRecords,
    SUM(TotalMinutesAsleep) AS TotalMinutesAsleep,
    SUM(TotalTimeInBed) AS TotalTimeInBed
FROM filtered
GROUP BY Id, SleepDay;

-- ---------------------------------------------------------------------
-- Weight log: de-duplicate only. Fat is left NULL where missing rather
-- than imputed (see cleaning.py docstring for the same decision).
-- ---------------------------------------------------------------------
CREATE VIEW clean_weight_log AS
SELECT DISTINCT * FROM raw_weight_log;

-- ---------------------------------------------------------------------
-- Hourly tables: de-duplicate and drop negative values.
-- ---------------------------------------------------------------------
CREATE VIEW clean_hourly_steps AS
WITH deduped AS (SELECT DISTINCT * FROM raw_hourly_steps),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY Id, ActivityHour) AS rn
    FROM deduped
)
SELECT Id, ActivityHour, StepTotal
FROM ranked
WHERE rn = 1 AND StepTotal >= 0;

CREATE VIEW clean_hourly_calories AS
WITH deduped AS (SELECT DISTINCT * FROM raw_hourly_calories),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY Id, ActivityHour) AS rn
    FROM deduped
)
SELECT Id, ActivityHour, Calories
FROM ranked
WHERE rn = 1 AND Calories >= 0;

CREATE VIEW clean_hourly_intensities AS
WITH deduped AS (SELECT DISTINCT * FROM raw_hourly_intensities),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY Id, ActivityHour) AS rn
    FROM deduped
)
SELECT Id, ActivityHour, TotalIntensity, AverageIntensity
FROM ranked
WHERE rn = 1 AND TotalIntensity >= 0;
