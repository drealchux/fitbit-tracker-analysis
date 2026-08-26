-- Device usage frequency and user segmentation: SQL equivalent of
-- analysis.device_usage_frequency() and (a simplified version of)
-- segmentation.segment_users().
--
-- Note on segmentation: the Python pipeline uses k-means clustering on
-- four standardized features (see src/bellabeat/segmentation.py), which
-- is not practical to replicate exactly in standard SQL. This file
-- instead assigns users to "Low activity" / "High activity" by whether
-- their average daily steps fall below or at-or-above the population
-- median, a transparent one-dimensional rule any BI tool can reproduce.
-- Treat the Python k-means result as authoritative; this SQL version is
-- for teams that only have SQL/BI tooling available and need a directional
-- answer to "are there distinct groups of users."
--
-- Run after sql/transform_views.sql:
--   sqlite3 data_processed/bellabeat.db < sql/device_usage_and_segments.sql

-- ---------------------------------------------------------------------
-- Device usage frequency tiers (days with any recorded activity, of 31).
-- ---------------------------------------------------------------------
SELECT
    device_usage_days,
    device_usage_rate_pct,
    CASE
        WHEN device_usage_days <= 10 THEN 'Low use (<=10 days)'
        WHEN device_usage_days <= 20 THEN 'Moderate use (11-20 days)'
        WHEN device_usage_days <= 27 THEN 'High use (21-27 days)'
        ELSE 'Near-daily use (28-31 days)'
    END AS usage_frequency_tier
FROM user_summary
ORDER BY device_usage_days DESC;

SELECT
    CASE
        WHEN device_usage_days <= 10 THEN 'Low use (<=10 days)'
        WHEN device_usage_days <= 20 THEN 'Moderate use (11-20 days)'
        WHEN device_usage_days <= 27 THEN 'High use (21-27 days)'
        ELSE 'Near-daily use (28-31 days)'
    END AS usage_frequency_tier,
    COUNT(*) AS n_users
FROM user_summary
GROUP BY usage_frequency_tier
ORDER BY n_users DESC;

-- ---------------------------------------------------------------------
-- Rule-based two-group segmentation on median daily steps.
-- ---------------------------------------------------------------------
WITH median_steps AS (
    SELECT AVG(avg_daily_steps) AS med
    FROM (
        SELECT avg_daily_steps,
               ROW_NUMBER() OVER (ORDER BY avg_daily_steps) AS rn,
               COUNT(*) OVER () AS cnt
        FROM user_summary
        WHERE avg_daily_steps IS NOT NULL
    )
    WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
)
SELECT
    CASE WHEN u.avg_daily_steps >= m.med THEN 'High activity' ELSE 'Low activity' END AS segment,
    COUNT(*) AS n_users,
    ROUND(AVG(u.avg_daily_steps), 1) AS avg_daily_steps,
    ROUND(AVG(u.avg_sedentary_minutes), 1) AS avg_sedentary_minutes,
    ROUND(AVG(u.avg_active_minutes), 1) AS avg_active_minutes,
    ROUND(AVG(u.avg_daily_calories), 1) AS avg_daily_calories,
    ROUND(AVG(u.device_usage_days), 1) AS avg_device_usage_days
FROM user_summary u, median_steps m
WHERE u.avg_daily_steps IS NOT NULL
GROUP BY segment;
