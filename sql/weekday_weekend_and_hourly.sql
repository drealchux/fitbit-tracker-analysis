-- Weekday/weekend comparison and time-of-day usage patterns: SQL
-- equivalent of analysis.weekday_weekend_test(), weekday_activity_profile(),
-- and hourly_activity_profile().
--
-- Run after sql/transform_views.sql:
--   sqlite3 data_processed/bellabeat.db < sql/weekday_weekend_and_hourly.sql

-- ---------------------------------------------------------------------
-- Weekday vs. weekend group means (worn days). A full Welch's t-test
-- needs the exact p-value machinery used in sql/04 (see that file's
-- note); this reports the group means, sizes, and pooled-variance t
-- statistic so the direction and rough significance of any gap is visible
-- directly from SQL, with the Python pipeline's t-test as the exact result.
-- ---------------------------------------------------------------------
SELECT
    'Steps' AS metric,
    ROUND(AVG(CASE WHEN is_weekend = 0 THEN TotalSteps END), 1) AS weekday_mean,
    ROUND(AVG(CASE WHEN is_weekend = 1 THEN TotalSteps END), 1) AS weekend_mean,
    SUM(CASE WHEN is_weekend = 0 THEN 1 ELSE 0 END) AS weekday_n,
    SUM(CASE WHEN is_weekend = 1 THEN 1 ELSE 0 END) AS weekend_n
FROM user_day_master
WHERE is_non_wear_day = 0

UNION ALL

SELECT
    'SedentaryMinutes',
    ROUND(AVG(CASE WHEN is_weekend = 0 THEN SedentaryMinutes END), 1),
    ROUND(AVG(CASE WHEN is_weekend = 1 THEN SedentaryMinutes END), 1),
    SUM(CASE WHEN is_weekend = 0 THEN 1 ELSE 0 END),
    SUM(CASE WHEN is_weekend = 1 THEN 1 ELSE 0 END)
FROM user_day_master
WHERE is_non_wear_day = 0;

-- ---------------------------------------------------------------------
-- Average steps, active minutes, and sedentary minutes by day of week.
-- ---------------------------------------------------------------------
SELECT
    day_of_week,
    ROUND(AVG(TotalSteps), 1) AS avg_steps,
    ROUND(AVG(total_active_minutes), 1) AS avg_active_minutes,
    ROUND(AVG(SedentaryMinutes), 1) AS avg_sedentary_minutes,
    COUNT(*) AS n_days
FROM user_day_master
WHERE is_non_wear_day = 0
GROUP BY day_of_week
ORDER BY
    CASE day_of_week
        WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END;

-- ---------------------------------------------------------------------
-- Average steps and calories by hour of day, weekday vs. weekend.
-- ---------------------------------------------------------------------
SELECT
    is_weekend,
    hour_of_day,
    ROUND(AVG(StepTotal), 1) AS avg_steps,
    ROUND(AVG(Calories), 1) AS avg_calories
FROM hourly_usage
GROUP BY is_weekend, hour_of_day
ORDER BY is_weekend, hour_of_day;
