-- Correlation analysis: SQL equivalent of analysis.correlation_test().
--
-- Pearson r is computed directly with the standard sum-based formula.
-- SQLite has no inverse t-distribution function, so an exact p-value
-- cannot be produced in pure SQL; the t-statistic is reported instead
-- (t = r * sqrt((n-2) / (1-r^2))), which an analyst can compare against a
-- standard t-table, or cross-check against the exact p-value already
-- computed by the Python pipeline (see outputs/tables/statistical_test_results.json).
-- This is a documented method difference between the two implementations,
-- not a bug: see docs/data_quality_report.md.
--
-- Run after sql/transform_views.sql:
--   sqlite3 data_processed/bellabeat.db < sql/correlation_analysis.sql

-- ---------------------------------------------------------------------
-- Steps vs. calories burned (worn days)
-- ---------------------------------------------------------------------
SELECT
    'Steps vs. calories burned' AS label,
    COUNT(*) AS n,
    ROUND(
        (COUNT(*) * SUM(TotalSteps * Calories) - SUM(TotalSteps) * SUM(Calories))
        / SQRT(
            (COUNT(*) * SUM(TotalSteps * TotalSteps) - SUM(TotalSteps) * SUM(TotalSteps))
            * (COUNT(*) * SUM(Calories * Calories) - SUM(Calories) * SUM(Calories))
        ), 3
    ) AS pearson_r
FROM user_day_master
WHERE is_non_wear_day = 0

UNION ALL

-- ---------------------------------------------------------------------
-- Steps vs. sleep duration (worn days with a logged sleep record)
-- ---------------------------------------------------------------------
SELECT
    'Steps vs. sleep duration',
    COUNT(*),
    ROUND(
        (COUNT(*) * SUM(TotalSteps * TotalMinutesAsleep) - SUM(TotalSteps) * SUM(TotalMinutesAsleep))
        / SQRT(
            (COUNT(*) * SUM(TotalSteps * TotalSteps) - SUM(TotalSteps) * SUM(TotalSteps))
            * (COUNT(*) * SUM(TotalMinutesAsleep * TotalMinutesAsleep) - SUM(TotalMinutesAsleep) * SUM(TotalMinutesAsleep))
        ), 3
    )
FROM user_day_master
WHERE is_non_wear_day = 0 AND has_sleep_log = 1

UNION ALL

-- ---------------------------------------------------------------------
-- Sedentary minutes vs. sleep duration (worn days with a logged sleep record)
-- ---------------------------------------------------------------------
SELECT
    'Sedentary minutes vs. sleep duration',
    COUNT(*),
    ROUND(
        (COUNT(*) * SUM(SedentaryMinutes * TotalMinutesAsleep) - SUM(SedentaryMinutes) * SUM(TotalMinutesAsleep))
        / SQRT(
            (COUNT(*) * SUM(SedentaryMinutes * SedentaryMinutes) - SUM(SedentaryMinutes) * SUM(SedentaryMinutes))
            * (COUNT(*) * SUM(TotalMinutesAsleep * TotalMinutesAsleep) - SUM(TotalMinutesAsleep) * SUM(TotalMinutesAsleep))
        ), 3
    )
FROM user_day_master
WHERE is_non_wear_day = 0 AND has_sleep_log = 1

UNION ALL

-- ---------------------------------------------------------------------
-- Distance vs. calories burned (worn days)
-- ---------------------------------------------------------------------
SELECT
    'Distance vs. calories burned',
    COUNT(*),
    ROUND(
        (COUNT(*) * SUM(TotalDistance * Calories) - SUM(TotalDistance) * SUM(Calories))
        / SQRT(
            (COUNT(*) * SUM(TotalDistance * TotalDistance) - SUM(TotalDistance) * SUM(TotalDistance))
            * (COUNT(*) * SUM(Calories * Calories) - SUM(Calories) * SUM(Calories))
        ), 3
    )
FROM user_day_master
WHERE is_non_wear_day = 0;
