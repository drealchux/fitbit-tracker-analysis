"""Data cleaning and quality-check functions (the "Process" phase).

Every cleaning function returns a tuple of (cleaned_dataframe, report)
where report is a plain dict of counts describing what was found and what
was done. The report dicts are collected by scripts/run_pipeline.py into
docs/data_quality_report.md so the cleaning process is fully auditable
without re-reading the code.

Design principle: never silently drop data. Every row that is removed or
flagged is counted and explained in the returned report.
"""

from __future__ import annotations

import logging

import pandas as pd

from . import config

logger = logging.getLogger(__name__)


def clean_daily_activity(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean dailyActivity_merged.

    Checks performed:
      * exact duplicate rows
      * duplicate (Id, ActivityDate) combinations (should be unique keys)
      * impossible values (negative or implausibly large steps/calories)
      * non-wear days: 0 steps and 1440 sedentary minutes, which almost
        certainly means the device was not worn rather than the user being
        perfectly sedentary for 24 hours. These rows are kept (deleting
        them would understate non-wear rates) but flagged with an
        `is_non_wear_day` column so downstream analysis can exclude them
        from "how active are users" questions while still counting them
        for "how often do users wear the device" questions.
    """
    report: dict = {"table": "daily_activity", "input_rows": len(df)}

    exact_dupes = df.duplicated().sum()
    df = df.drop_duplicates()
    report["exact_duplicate_rows_dropped"] = int(exact_dupes)

    key_dupes = df.duplicated(subset=["Id", "ActivityDate"]).sum()
    if key_dupes:
        df = df.drop_duplicates(subset=["Id", "ActivityDate"], keep="first")
    report["duplicate_id_date_rows_dropped"] = int(key_dupes)

    impossible_steps = df["TotalSteps"] > config.MAX_PLAUSIBLE_STEPS_PER_DAY
    impossible_calories = (df["Calories"] > config.MAX_PLAUSIBLE_CALORIES_PER_DAY) | (
        (df["Calories"] < config.MIN_PLAUSIBLE_CALORIES_PER_DAY) & (df["Calories"] > 0)
    )
    negative_values = (
        (df["TotalSteps"] < 0)
        | (df["Calories"] < 0)
        | (df["SedentaryMinutes"] < 0)
        | (df["VeryActiveMinutes"] < 0)
    )
    report["rows_with_implausible_steps"] = int(impossible_steps.sum())
    report["rows_with_implausible_calories"] = int(impossible_calories.sum())
    report["rows_with_negative_values"] = int(negative_values.sum())
    # None found in this dataset as of analysis time; kept as an explicit
    # check rather than a silent assumption. If found, they would be
    # dropped here rather than passed downstream.
    df = df[~negative_values].copy()

    non_wear = (df["TotalSteps"] == 0) & (df["SedentaryMinutes"] == config.MINUTES_PER_DAY)
    df["is_non_wear_day"] = non_wear
    report["non_wear_days_flagged"] = int(non_wear.sum())

    minutes_logged = (
        df["VeryActiveMinutes"]
        + df["FairlyActiveMinutes"]
        + df["LightlyActiveMinutes"]
        + df["SedentaryMinutes"]
    )
    report["rows_with_minutes_over_1440"] = int((minutes_logged > config.MINUTES_PER_DAY).sum())

    report["output_rows"] = len(df)
    report["unique_users"] = int(df["Id"].nunique())
    report["date_min"] = str(df["ActivityDate"].min().date())
    report["date_max"] = str(df["ActivityDate"].max().date())

    logger.info("Cleaned daily_activity: %s", report)
    return df, report


def clean_sleep_day(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean sleepDay_merged.

    In this export, sleepDay already ships as (nearly) one row per user-day:
    TotalSleepRecords counts how many sleep sessions (e.g. a nap plus an
    overnight sleep) were rolled into that day's totals, rather than each
    session appearing as its own row. After exact duplicate rows are
    removed, the table is grouped and summed by (Id, SleepDay) as a
    defensive step: this is a no-op on the current export (every Id/day
    pair is already unique post-dedup) but keeps the function correct if a
    future export ever does deliver multiple rows for the same user-day.
    """
    report: dict = {"table": "sleep_day", "input_rows": len(df)}

    exact_dupes = df.duplicated().sum()
    df = df.drop_duplicates()
    report["exact_duplicate_rows_dropped"] = int(exact_dupes)

    implausible = (df["TotalMinutesAsleep"] > config.MAX_PLAUSIBLE_SLEEP_MINUTES) | (
        df["TotalMinutesAsleep"] < config.MIN_PLAUSIBLE_SLEEP_MINUTES
    )
    report["rows_with_implausible_sleep_minutes"] = int(implausible.sum())
    df = df[~implausible].copy()

    inconsistent_bed_time = df["TotalTimeInBed"] < df["TotalMinutesAsleep"]
    report["rows_time_in_bed_less_than_asleep"] = int(inconsistent_bed_time.sum())
    df = df[~inconsistent_bed_time].copy()

    multi_session_days_before_agg = int((df["TotalSleepRecords"] > 1).sum())
    report["multi_session_day_rows_before_aggregation"] = multi_session_days_before_agg

    daily = (
        df.groupby(["Id", "SleepDay"], as_index=False)
        .agg(
            TotalSleepRecords=("TotalSleepRecords", "sum"),
            TotalMinutesAsleep=("TotalMinutesAsleep", "sum"),
            TotalTimeInBed=("TotalTimeInBed", "sum"),
        )
    )

    report["output_rows"] = len(daily)
    report["unique_users"] = int(daily["Id"].nunique())
    report["date_min"] = str(daily["SleepDay"].min().date())
    report["date_max"] = str(daily["SleepDay"].max().date())

    logger.info("Cleaned sleep_day: %s", report)
    return daily, report


def clean_weight_log(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean weightLogInfo_merged.

    Fat is missing for the large majority of rows (only manually entered by
    users on a body-fat scale), so it is not imputed; it is simply excluded
    from any aggregate that would be biased by the missingness. WeightKg is
    complete and used as the primary weight metric.
    """
    report: dict = {"table": "weight_log", "input_rows": len(df)}

    exact_dupes = df.duplicated().sum()
    df = df.drop_duplicates()
    report["exact_duplicate_rows_dropped"] = int(exact_dupes)

    report["missing_fat_pct"] = round(100 * df["Fat"].isnull().mean(), 1)
    report["output_rows"] = len(df)
    report["unique_users"] = int(df["Id"].nunique())
    report["manual_report_share_pct"] = round(100 * df["IsManualReport"].mean(), 1)

    logger.info("Cleaned weight_log: %s", report)
    return df, report


def clean_hourly(df: pd.DataFrame, value_col: str, table_name: str) -> tuple[pd.DataFrame, dict]:
    """Generic cleaner for the hourlySteps / hourlyCalories / hourlyIntensities tables."""
    report: dict = {"table": table_name, "input_rows": len(df)}

    exact_dupes = df.duplicated().sum()
    df = df.drop_duplicates()
    report["exact_duplicate_rows_dropped"] = int(exact_dupes)

    key_dupes = df.duplicated(subset=["Id", "ActivityHour"]).sum()
    if key_dupes:
        df = df.drop_duplicates(subset=["Id", "ActivityHour"], keep="first")
    report["duplicate_id_hour_rows_dropped"] = int(key_dupes)

    negative_values = df[value_col] < 0
    report["rows_with_negative_values"] = int(negative_values.sum())
    df = df[~negative_values].copy()

    report["output_rows"] = len(df)
    report["unique_users"] = int(df["Id"].nunique())

    logger.info("Cleaned %s: %s", table_name, report)
    return df, report
