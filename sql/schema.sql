-- Schema reference for the raw tables loaded by scripts/build_sqlite_db.py.
--
-- This file is documentation, not something you need to run: the loader
-- script creates these tables from the CSVs directly via pandas.to_sql,
-- inferring the same column types shown here. It is included so a reader
-- (or a BI tool that needs an explicit schema) can see the raw structure
-- without opening a CSV.
--
-- Source: Fitabase export "4.12.16-5.12.16" (33 users, 31 days). See
-- docs/data_quality_report.md for why this export was chosen over the
-- overlapping 3.12.16-4.11.16 export.

-- One row per user per day.
CREATE TABLE IF NOT EXISTS raw_daily_activity (
    Id                          INTEGER NOT NULL,
    ActivityDate                TEXT NOT NULL,   -- ISO 8601 'YYYY-MM-DD HH:MM:SS'
    TotalSteps                  INTEGER NOT NULL,
    TotalDistance                REAL NOT NULL,
    TrackerDistance              REAL NOT NULL,
    LoggedActivitiesDistance     REAL NOT NULL,
    VeryActiveDistance           REAL NOT NULL,
    ModeratelyActiveDistance     REAL NOT NULL,
    LightActiveDistance          REAL NOT NULL,
    SedentaryActiveDistance      REAL NOT NULL,
    VeryActiveMinutes           INTEGER NOT NULL,
    FairlyActiveMinutes         INTEGER NOT NULL,
    LightlyActiveMinutes        INTEGER NOT NULL,
    SedentaryMinutes            INTEGER NOT NULL,
    Calories                    INTEGER NOT NULL
);

-- One row per user per day (sessions on the same day are pre-summed by
-- Fitabase; TotalSleepRecords counts how many sessions were rolled in).
CREATE TABLE IF NOT EXISTS raw_sleep_day (
    Id                  INTEGER NOT NULL,
    SleepDay             TEXT NOT NULL,
    TotalSleepRecords   INTEGER NOT NULL,
    TotalMinutesAsleep  INTEGER NOT NULL,
    TotalTimeInBed      INTEGER NOT NULL
);

-- One row per user per hour.
CREATE TABLE IF NOT EXISTS raw_hourly_steps (
    Id            INTEGER NOT NULL,
    ActivityHour   TEXT NOT NULL,
    StepTotal     INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_hourly_calories (
    Id            INTEGER NOT NULL,
    ActivityHour   TEXT NOT NULL,
    Calories      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_hourly_intensities (
    Id                INTEGER NOT NULL,
    ActivityHour       TEXT NOT NULL,
    TotalIntensity    INTEGER NOT NULL,
    AverageIntensity   REAL NOT NULL
);

-- Sparse: only 8 of 33 users ever logged a weight entry.
CREATE TABLE IF NOT EXISTS raw_weight_log (
    Id                INTEGER NOT NULL,
    Date               TEXT NOT NULL,
    WeightKg           REAL NOT NULL,
    WeightPounds        REAL NOT NULL,
    Fat                 REAL,            -- mostly NULL; manually entered
    BMI                 REAL NOT NULL,
    IsManualReport      INTEGER NOT NULL, -- 0/1
    LogId               INTEGER NOT NULL
);
