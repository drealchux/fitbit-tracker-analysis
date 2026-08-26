-- Transform views: SQL equivalent of src/bellabeat/transform.py.
--
-- Run after sql/cleaning_views.sql.
--   sqlite3 data_processed/bellabeat.db < sql/transform_views.sql

DROP VIEW IF EXISTS activity_with_derived_fields;
DROP VIEW IF EXISTS user_day_master;
DROP VIEW IF EXISTS user_summary;
DROP VIEW IF EXISTS hourly_usage;

-- ---------------------------------------------------------------------
-- Derived per-day activity fields (see add_activity_derived_fields).
-- ---------------------------------------------------------------------
CREATE VIEW activity_with_derived_fields AS
SELECT
    *,
    VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes AS total_active_minutes,
    (VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes + SedentaryMinutes) AS total_logged_minutes,
    CASE
        WHEN (VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes + SedentaryMinutes) > 0
        THEN 100.0 * SedentaryMinutes / (VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes + SedentaryMinutes)
        ELSE NULL
    END AS sedentary_share_pct,
    CASE
        WHEN TotalSteps < 5000 THEN 'Sedentary (<5,000)'
        WHEN TotalSteps < 7500 THEN 'Low active (5,000-7,499)'
        WHEN TotalSteps < 10000 THEN 'Somewhat active (7,500-9,999)'
        WHEN TotalSteps < 12500 THEN 'Active (10,000-12,499)'
        ELSE 'Highly active (12,500+)'
    END AS activity_tier
FROM clean_daily_activity;

-- ---------------------------------------------------------------------
-- One row per user-day: activity left-joined with sleep (see
-- build_user_day_master docstring for why the join is left, not inner),
-- plus calendar fields (day name, weekend flag).
-- ---------------------------------------------------------------------
CREATE VIEW user_day_master AS
SELECT
    a.Id,
    a.ActivityDate,
    a.TotalSteps,
    a.TotalDistance,
    a.VeryActiveDistance,
    a.ModeratelyActiveDistance,
    a.LightActiveDistance,
    a.VeryActiveMinutes,
    a.FairlyActiveMinutes,
    a.LightlyActiveMinutes,
    a.SedentaryMinutes,
    a.Calories,
    a.is_non_wear_day,
    a.total_active_minutes,
    a.sedentary_share_pct,
    a.activity_tier,
    s.TotalSleepRecords,
    s.TotalMinutesAsleep,
    s.TotalTimeInBed,
    CASE WHEN s.TotalMinutesAsleep IS NOT NULL THEN 1 ELSE 0 END AS has_sleep_log,
    CASE strftime('%w', a.ActivityDate)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS day_of_week,
    CASE WHEN strftime('%w', a.ActivityDate) IN ('0', '6') THEN 1 ELSE 0 END AS is_weekend
FROM activity_with_derived_fields a
LEFT JOIN clean_sleep_day s
    ON a.Id = s.Id AND a.ActivityDate = s.SleepDay;

-- ---------------------------------------------------------------------
-- One row per user: usage frequency (all logged days) and activity /
-- sleep averages (worn days only for activity, logged nights only for
-- sleep), matching build_user_summary.
-- ---------------------------------------------------------------------
CREATE VIEW user_summary AS
WITH usage AS (
    SELECT
        Id,
        COUNT(*) AS device_usage_days,
        ROUND(100.0 * COUNT(*) / 31, 1) AS device_usage_rate_pct
    FROM user_day_master
    GROUP BY Id
),
activity AS (
    SELECT
        Id,
        ROUND(AVG(TotalSteps), 0) AS avg_daily_steps,
        ROUND(AVG(Calories), 0) AS avg_daily_calories,
        ROUND(AVG(SedentaryMinutes), 1) AS avg_sedentary_minutes,
        ROUND(AVG(total_active_minutes), 1) AS avg_active_minutes,
        ROUND(AVG(VeryActiveMinutes), 1) AS avg_very_active_minutes,
        ROUND(AVG(TotalDistance), 2) AS avg_distance_km,
        COUNT(*) AS active_days
    FROM user_day_master
    WHERE is_non_wear_day = 0
    GROUP BY Id
),
sleep AS (
    SELECT
        Id,
        ROUND(AVG(TotalMinutesAsleep), 0) AS avg_sleep_minutes,
        COUNT(*) AS sleep_days_logged
    FROM user_day_master
    WHERE has_sleep_log = 1
    GROUP BY Id
)
SELECT
    u.Id,
    u.device_usage_days,
    u.device_usage_rate_pct,
    a.avg_daily_steps,
    a.avg_daily_calories,
    a.avg_sedentary_minutes,
    a.avg_active_minutes,
    a.avg_very_active_minutes,
    a.avg_distance_km,
    a.active_days,
    sl.avg_sleep_minutes,
    ROUND(sl.avg_sleep_minutes / 60.0, 1) AS avg_sleep_hours,
    sl.sleep_days_logged
FROM usage u
LEFT JOIN activity a ON u.Id = a.Id
LEFT JOIN sleep sl ON u.Id = sl.Id;

-- ---------------------------------------------------------------------
-- Hourly usage: merge the three hourly tables and add hour/weekday fields.
-- ---------------------------------------------------------------------
CREATE VIEW hourly_usage AS
SELECT
    hs.Id,
    hs.ActivityHour,
    hs.StepTotal,
    hc.Calories,
    hi.TotalIntensity,
    hi.AverageIntensity,
    CAST(strftime('%H', hs.ActivityHour) AS INTEGER) AS hour_of_day,
    CASE strftime('%w', hs.ActivityHour)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS day_of_week,
    CASE WHEN strftime('%w', hs.ActivityHour) IN ('0', '6') THEN 1 ELSE 0 END AS is_weekend
FROM clean_hourly_steps hs
JOIN clean_hourly_calories hc ON hs.Id = hc.Id AND hs.ActivityHour = hc.ActivityHour
JOIN clean_hourly_intensities hi ON hs.Id = hi.Id AND hs.ActivityHour = hi.ActivityHour;
