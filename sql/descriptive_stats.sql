-- Descriptive statistics: SQL equivalent of analysis.describe_numeric().
--
-- Median and percentiles use the nearest-rank method via window functions
-- (SQLite has no built-in PERCENTILE_CONT). This will not match pandas'
-- linear-interpolation percentiles to the decimal, only approximately;
-- see docs/data_quality_report.md for this documented method difference.
-- Standard deviation is sample standard deviation (n-1 denominator), to
-- match pandas' default ddof=1.
--
-- Every metric's ranked rows are named CTEs (not inline "FROM (...) AS x"
-- subqueries), because a correlated subquery cannot re-open a sibling
-- FROM-clause alias by name in SQLite; a named CTE can.
--
-- Run after sql/transform_views.sql:
--   sqlite3 data_processed/bellabeat.db < sql/descriptive_stats.sql

WITH
ordered_steps AS (
    SELECT TotalSteps AS val, ROW_NUMBER() OVER (ORDER BY TotalSteps) AS rn, COUNT(*) OVER () AS cnt
    FROM user_day_master WHERE is_non_wear_day = 0
),
ordered_calories AS (
    SELECT Calories AS val, ROW_NUMBER() OVER (ORDER BY Calories) AS rn, COUNT(*) OVER () AS cnt
    FROM user_day_master WHERE is_non_wear_day = 0
),
ordered_sedentary AS (
    SELECT SedentaryMinutes AS val, ROW_NUMBER() OVER (ORDER BY SedentaryMinutes) AS rn, COUNT(*) OVER () AS cnt
    FROM user_day_master WHERE is_non_wear_day = 0
),
ordered_active AS (
    SELECT total_active_minutes AS val, ROW_NUMBER() OVER (ORDER BY total_active_minutes) AS rn, COUNT(*) OVER () AS cnt
    FROM user_day_master WHERE is_non_wear_day = 0
),
ordered_distance AS (
    SELECT TotalDistance AS val, ROW_NUMBER() OVER (ORDER BY TotalDistance) AS rn, COUNT(*) OVER () AS cnt
    FROM user_day_master WHERE is_non_wear_day = 0
),
-- Sleep metrics (nights with a logged sleep record only)
ordered_sleep AS (
    SELECT TotalMinutesAsleep AS val, ROW_NUMBER() OVER (ORDER BY TotalMinutesAsleep) AS rn, COUNT(*) OVER () AS cnt
    FROM user_day_master WHERE has_sleep_log = 1
),
ordered_time_in_bed AS (
    SELECT TotalTimeInBed AS val, ROW_NUMBER() OVER (ORDER BY TotalTimeInBed) AS rn, COUNT(*) OVER () AS cnt
    FROM user_day_master WHERE has_sleep_log = 1
)
SELECT
    'TotalSteps' AS metric, MAX(cnt) AS n, ROUND(AVG(val), 1) AS mean,
    ROUND((SELECT AVG(val) FROM ordered_steps WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)), 2) AS median,
    ROUND(SQRT(SUM((val - (SELECT AVG(val) FROM ordered_steps)) * (val - (SELECT AVG(val) FROM ordered_steps))) / (MAX(cnt) - 1.0)), 1) AS std,
    ROUND(MIN(val), 2) AS min,
    ROUND((SELECT val FROM ordered_steps WHERE rn = CAST((0.25 * cnt) + 1 AS INTEGER)), 2) AS p25,
    ROUND((SELECT val FROM ordered_steps WHERE rn = CAST((0.75 * cnt) + 1 AS INTEGER)), 2) AS p75,
    ROUND(MAX(val), 2) AS max
FROM ordered_steps

UNION ALL

SELECT
    'Calories', MAX(cnt), ROUND(AVG(val), 1),
    ROUND((SELECT AVG(val) FROM ordered_calories WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)), 2),
    ROUND(SQRT(SUM((val - (SELECT AVG(val) FROM ordered_calories)) * (val - (SELECT AVG(val) FROM ordered_calories))) / (MAX(cnt) - 1.0)), 1),
    ROUND(MIN(val), 2),
    ROUND((SELECT val FROM ordered_calories WHERE rn = CAST((0.25 * cnt) + 1 AS INTEGER)), 2),
    ROUND((SELECT val FROM ordered_calories WHERE rn = CAST((0.75 * cnt) + 1 AS INTEGER)), 2),
    ROUND(MAX(val), 2)
FROM ordered_calories

UNION ALL

SELECT
    'SedentaryMinutes', MAX(cnt), ROUND(AVG(val), 1),
    ROUND((SELECT AVG(val) FROM ordered_sedentary WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)), 2),
    ROUND(SQRT(SUM((val - (SELECT AVG(val) FROM ordered_sedentary)) * (val - (SELECT AVG(val) FROM ordered_sedentary))) / (MAX(cnt) - 1.0)), 1),
    ROUND(MIN(val), 2),
    ROUND((SELECT val FROM ordered_sedentary WHERE rn = CAST((0.25 * cnt) + 1 AS INTEGER)), 2),
    ROUND((SELECT val FROM ordered_sedentary WHERE rn = CAST((0.75 * cnt) + 1 AS INTEGER)), 2),
    ROUND(MAX(val), 2)
FROM ordered_sedentary

UNION ALL

SELECT
    'total_active_minutes', MAX(cnt), ROUND(AVG(val), 1),
    ROUND((SELECT AVG(val) FROM ordered_active WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)), 2),
    ROUND(SQRT(SUM((val - (SELECT AVG(val) FROM ordered_active)) * (val - (SELECT AVG(val) FROM ordered_active))) / (MAX(cnt) - 1.0)), 1),
    ROUND(MIN(val), 2),
    ROUND((SELECT val FROM ordered_active WHERE rn = CAST((0.25 * cnt) + 1 AS INTEGER)), 2),
    ROUND((SELECT val FROM ordered_active WHERE rn = CAST((0.75 * cnt) + 1 AS INTEGER)), 2),
    ROUND(MAX(val), 2)
FROM ordered_active

UNION ALL

SELECT
    'TotalDistance', MAX(cnt), ROUND(AVG(val), 1),
    ROUND((SELECT AVG(val) FROM ordered_distance WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)), 2),
    ROUND(SQRT(SUM((val - (SELECT AVG(val) FROM ordered_distance)) * (val - (SELECT AVG(val) FROM ordered_distance))) / (MAX(cnt) - 1.0)), 1),
    ROUND(MIN(val), 2),
    ROUND((SELECT val FROM ordered_distance WHERE rn = CAST((0.25 * cnt) + 1 AS INTEGER)), 2),
    ROUND((SELECT val FROM ordered_distance WHERE rn = CAST((0.75 * cnt) + 1 AS INTEGER)), 2),
    ROUND(MAX(val), 2)
FROM ordered_distance

UNION ALL

SELECT
    'TotalMinutesAsleep', MAX(cnt), ROUND(AVG(val), 1),
    ROUND((SELECT AVG(val) FROM ordered_sleep WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)), 2),
    ROUND(SQRT(SUM((val - (SELECT AVG(val) FROM ordered_sleep)) * (val - (SELECT AVG(val) FROM ordered_sleep))) / (MAX(cnt) - 1.0)), 1),
    ROUND(MIN(val), 2),
    ROUND((SELECT val FROM ordered_sleep WHERE rn = CAST((0.25 * cnt) + 1 AS INTEGER)), 2),
    ROUND((SELECT val FROM ordered_sleep WHERE rn = CAST((0.75 * cnt) + 1 AS INTEGER)), 2),
    ROUND(MAX(val), 2)
FROM ordered_sleep

UNION ALL

SELECT
    'TotalTimeInBed', MAX(cnt), ROUND(AVG(val), 1),
    ROUND((SELECT AVG(val) FROM ordered_time_in_bed WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)), 2),
    ROUND(SQRT(SUM((val - (SELECT AVG(val) FROM ordered_time_in_bed)) * (val - (SELECT AVG(val) FROM ordered_time_in_bed))) / (MAX(cnt) - 1.0)), 1),
    ROUND(MIN(val), 2),
    ROUND((SELECT val FROM ordered_time_in_bed WHERE rn = CAST((0.25 * cnt) + 1 AS INTEGER)), 2),
    ROUND((SELECT val FROM ordered_time_in_bed WHERE rn = CAST((0.75 * cnt) + 1 AS INTEGER)), 2),
    ROUND(MAX(val), 2)
FROM ordered_time_in_bed;
