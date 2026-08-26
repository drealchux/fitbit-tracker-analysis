"""Descriptive and statistical analysis (the "Analyze" phase).

Every function returns plain Python / pandas structures (dicts, Series,
DataFrames) rather than printing, so results can be captured by the
pipeline script and written to docs and tables without re-running
anything. Statistical tests report the hypothesis, method, assumption
notes, and result together, per the project's analytical standards.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from . import config


def describe_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Mean, median, std, min, max, and key percentiles for a set of columns.

    Mean and median are both reported deliberately: fitness-tracker
    behavioral data is typically right-skewed (a few very active days or
    users pull the mean above the median), and comparing the two is the
    simplest available signal of that skew.
    """
    rows = []
    for col in columns:
        series = df[col].dropna()
        rows.append(
            {
                "metric": col,
                "n": int(series.count()),
                "mean": round(series.mean(), 1),
                "median": round(series.median(), 1),
                "std": round(series.std(), 1),
                "min": round(series.min(), 1),
                "p25": round(series.quantile(0.25), 1),
                "p75": round(series.quantile(0.75), 1),
                "max": round(series.max(), 1),
                "skew_mean_minus_median_pct": round(
                    100 * (series.mean() - series.median()) / series.median(), 1
                )
                if series.median()
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


def correlation_test(
    df: pd.DataFrame, col_x: str, col_y: str, label: str
) -> dict:
    """Pearson correlation with significance test between two numeric columns.

    Hypothesis: H0 is that there is no linear relationship (rho = 0)
    between col_x and col_y in the population these 33 users represent.
    Method: Pearson correlation coefficient with a two-sided t-test.
    Assumptions: both variables are approximately continuous and the
    relationship, if any, is approximately linear; with n well under 1,000
    user-days the test is sensitive to outliers, which is noted in the
    interpretation rather than corrected away.
    A significant result here describes association only. It is not
    evidence that one variable causes the other to change.
    """
    paired = df[[col_x, col_y]].dropna()
    r, p_value = stats.pearsonr(paired[col_x], paired[col_y])
    return {
        "label": label,
        "x": col_x,
        "y": col_y,
        "n": len(paired),
        "pearson_r": round(r, 3),
        "p_value": p_value,
        "significant_at_0.05": bool(p_value < 0.05),
        "r_squared": round(r**2, 3),
    }


def weekday_weekend_test(
    df: pd.DataFrame, value_col: str, label: str
) -> dict:
    """Welch's t-test comparing a metric between weekend and weekday days.

    Hypothesis: H0 is that the population mean of value_col is equal on
    weekends and weekdays. Method: Welch's two-sample t-test (does not
    assume equal variance between the two groups, which is safer than
    Student's t-test when group sizes and variances are not known to be
    equal). Assumption: approximate normality of each group's mean, which
    is reasonable at this sample size by the central limit theorem even
    though the underlying daily values are skewed.
    """
    weekday_vals = df.loc[~df["is_weekend"], value_col].dropna()
    weekend_vals = df.loc[df["is_weekend"], value_col].dropna()
    t_stat, p_value = stats.ttest_ind(weekday_vals, weekend_vals, equal_var=False)
    return {
        "label": label,
        "value_col": value_col,
        "weekday_mean": round(weekday_vals.mean(), 1),
        "weekend_mean": round(weekend_vals.mean(), 1),
        "weekday_n": len(weekday_vals),
        "weekend_n": len(weekend_vals),
        "t_stat": round(t_stat, 3),
        "p_value": p_value,
        "significant_at_0.05": bool(p_value < 0.05),
    }


def device_usage_frequency(user_summary: pd.DataFrame) -> pd.DataFrame:
    """Bucket users by how many of the 31 study days they logged activity."""
    bins = [-1, 10, 20, 27, 31]
    labels = ["Low use (<=10 days)", "Moderate use (11-20 days)", "High use (21-27 days)", "Near-daily use (28-31 days)"]
    result = user_summary.copy()
    result["usage_frequency_tier"] = pd.cut(
        result["device_usage_days"], bins=bins, labels=labels
    )
    return result


def activity_tier_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Count and share of rows in each Tudor-Locke & Bassett (2004) step tier.

    Works on either a day-level table (e.g. worn user-days, one row per
    user-day) or a user-level table (e.g. user_summary, one row per user)
    as long as it carries an `activity_tier` column built from
    config.STEP_TIER_BINS/LABELS (see transform.add_activity_derived_fields
    and transform.build_user_summary). The two granularities answer
    different questions -- "how many days were sedentary?" vs. "how many
    users are, on average, sedentary?" -- so are reported separately
    rather than combined.
    """
    counts = df["activity_tier"].value_counts().reindex(config.STEP_TIER_LABELS, fill_value=0)
    result = counts.rename("n").rename_axis("activity_tier").reset_index()
    result["pct"] = round(100 * result["n"] / result["n"].sum(), 1)
    return result


def hourly_activity_profile(hourly_usage: pd.DataFrame) -> pd.DataFrame:
    """Average steps and calories by hour of day, split by weekday/weekend."""
    return (
        hourly_usage.groupby(["is_weekend", "hour_of_day"])
        .agg(avg_steps=("StepTotal", "mean"), avg_calories=("Calories", "mean"))
        .reset_index()
    )


def weekday_activity_profile(user_day_master: pd.DataFrame) -> pd.DataFrame:
    """Average steps, active minutes, and sedentary minutes by day of week."""
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    profile = (
        user_day_master.groupby("day_of_week")
        .agg(
            avg_steps=("TotalSteps", "mean"),
            avg_active_minutes=("total_active_minutes", "mean"),
            avg_sedentary_minutes=("SedentaryMinutes", "mean"),
            n_days=("TotalSteps", "count"),
        )
        .reindex(order)
        .reset_index()
    )
    return profile
