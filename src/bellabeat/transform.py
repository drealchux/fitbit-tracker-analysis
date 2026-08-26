"""Feature engineering and table joins (the rest of the "Process" phase).

Functions here take cleaned tables from cleaning.py and produce the
analysis-ready tables consumed by analysis.py: a user-day master table,
a per-user summary table, and an hourly usage table.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from . import config

def add_calendar_fields(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Add weekday name, weekend flag, and ISO week number for a date column."""
    df = df.copy()
    df["day_of_week"] = df[date_col].dt.day_name()
    df["is_weekend"] = df[date_col].dt.dayofweek >= 5
    df["week_number"] = df[date_col].dt.isocalendar().week.astype(int)
    return df


def add_activity_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived activity metrics to the daily activity table.

    - total_active_minutes: very + fairly + lightly active minutes.
    - activity_tier: descriptive step-count bucket for segmentation and
      charting (see config.STEP_TIER_BINS for thresholds).
    - sedentary_share_pct: sedentary minutes as a share of all logged
      minutes, a device-usage-normalized measure of how sedentary a day
      was (robust to non-wear minutes not being logged at all).
    """
    df = df.copy()
    df["total_active_minutes"] = (
        df["VeryActiveMinutes"] + df["FairlyActiveMinutes"] + df["LightlyActiveMinutes"]
    )
    df["total_logged_minutes"] = df["total_active_minutes"] + df["SedentaryMinutes"]
    df["sedentary_share_pct"] = np.where(
        df["total_logged_minutes"] > 0,
        100 * df["SedentaryMinutes"] / df["total_logged_minutes"],
        np.nan,
    )
    df["activity_tier"] = pd.cut(
        df["TotalSteps"],
        bins=config.STEP_TIER_BINS,
        labels=config.STEP_TIER_LABELS,
    )
    return df


def build_user_day_master(
    daily_activity: pd.DataFrame, sleep_daily: pd.DataFrame
) -> pd.DataFrame:
    """Left-join sleep onto activity, keyed on (Id, date).
    A left join on activity is deliberate: activity is logged far more
    consistently than sleep (33 users vs. 24 users), and the business
    questions about steps, calories, and sedentary time should not be
    restricted to the subset of days a user also logged sleep. Rows
    without a sleep match simply carry NaN sleep columns.
    """
    sleep_renamed = sleep_daily.rename(columns={"SleepDay": "ActivityDate"})
    merged = daily_activity.merge(
        sleep_renamed, on=["Id", "ActivityDate"], how="left", validate="one_to_one"
    )
    merged["has_sleep_log"] = merged["TotalMinutesAsleep"].notna()
    merged = add_calendar_fields(merged, "ActivityDate")
    return merged


def build_user_summary(user_day_master: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the user-day master table into one row per user.
    device_usage_days: number of days the user has any activity record at
    all (worn or not), used as a proxy for how many days the device was
    set up / synced.
    active_days: days excluding flagged non-wear days, used for the
    activity-level averages so non-wear days do not drag down the mean.
    """
    worn = user_day_master[~user_day_master["is_non_wear_day"]]

    usage = user_day_master.groupby("Id").agg(
        device_usage_days=("ActivityDate", "count"),
    )
    usage["device_usage_rate_pct"] = round(
        100 * usage["device_usage_days"] / config.STUDY_PERIOD_DAYS, 1
    )

    activity = worn.groupby("Id").agg(
        avg_daily_steps=("TotalSteps", "mean"),
        median_daily_steps=("TotalSteps", "median"),
        avg_daily_calories=("Calories", "mean"),
        avg_sedentary_minutes=("SedentaryMinutes", "mean"),
        avg_active_minutes=("total_active_minutes", "mean"),
        avg_very_active_minutes=("VeryActiveMinutes", "mean"),
        avg_distance_km=("TotalDistance", "mean"),
        active_days=("ActivityDate", "count"),
    )

    sleep = user_day_master[user_day_master["has_sleep_log"]].groupby("Id").agg(
        avg_sleep_minutes=("TotalMinutesAsleep", "mean"),
        sleep_days_logged=("TotalMinutesAsleep", "count"),
        sleep_minutes_std=("TotalMinutesAsleep", "std"),
    )

    summary = usage.join(activity, how="left").join(sleep, how="left")
    summary = summary.reset_index()
    summary["avg_daily_steps"] = summary["avg_daily_steps"].round(0)
    summary["avg_daily_calories"] = summary["avg_daily_calories"].round(0)
    summary["avg_sleep_minutes"] = summary["avg_sleep_minutes"].round(0)
    summary["avg_sleep_hours"] = round(summary["avg_sleep_minutes"] / 60, 1)

    summary["activity_tier"] = pd.cut(
        summary["avg_daily_steps"],
        bins=config.STEP_TIER_BINS,
        labels=config.STEP_TIER_LABELS,
    )

    return summary


def build_hourly_usage(
    hourly_steps: pd.DataFrame, hourly_calories: pd.DataFrame, hourly_intensities: pd.DataFrame
) -> pd.DataFrame:
    """Merge the three hourly tables into one and add hour-of-day / weekday fields."""
    merged = hourly_steps.merge(
        hourly_calories, on=["Id", "ActivityHour"], how="inner", validate="one_to_one"
    ).merge(hourly_intensities, on=["Id", "ActivityHour"], how="inner", validate="one_to_one")

    merged["hour_of_day"] = merged["ActivityHour"].dt.hour
    merged["day_of_week"] = merged["ActivityHour"].dt.day_name()
    merged["is_weekend"] = merged["ActivityHour"].dt.dayofweek >= 5
    merged["date"] = merged["ActivityHour"].dt.date
    return merged
