"""Chart generation for the Share phase.

Every chart function saves a PNG to outputs/figures and returns the path.
Charts are deliberately limited to ones that answer a specific business
question from the case study brief; see docs/insights_and_recommendations.md
for the interpretation attached to each one.

Style choices: a small, consistent, colorblind-safe palette; no 3D or
decorative effects; units in every axis label; a title framed as the
question the chart answers rather than a generic description of its type.
"""

from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from . import config

PALETTE = {
    "primary": "#2E5266",
    "secondary": "#6E8898",
    "accent": "#D68C45",
    "muted": "#9FB8AD",
    "highlight": "#C1443C",
}
SEGMENT_PALETTE = ["#9FB8AD", "#6E8898", "#2E5266", "#1B3A4B"]
sns.set_theme(style="whitegrid", rc={"axes.edgecolor": "#CCCCCC"})


def _save(fig: plt.Figure, filename: str) -> Path:
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = config.FIGURES_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=config.FIGURE_DPI)
    plt.close(fig)
    return path


def plot_daily_steps_distribution(user_day_master: pd.DataFrame) -> Path:
    worn = user_day_master[~user_day_master["is_non_wear_day"]]
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(worn["TotalSteps"], bins=30, color=PALETTE["primary"], ax=ax)
    mean_steps = worn["TotalSteps"].mean()
    median_steps = worn["TotalSteps"].median()
    ax.axvline(mean_steps, color=PALETTE["highlight"], linestyle="--", label=f"Mean: {mean_steps:,.0f}")
    ax.axvline(median_steps, color=PALETTE["accent"], linestyle="--", label=f"Median: {median_steps:,.0f}")
    ax.set_title("How active are users on a typical worn day?\nDistribution of total daily steps")
    ax.set_xlabel("Total steps per day")
    ax.set_ylabel("Number of user-days")
    ax.legend()
    return _save(fig, "daily_steps_distribution.png")


def plot_sleep_duration_distribution(user_day_master: pd.DataFrame) -> Path:
    sleep = user_day_master[user_day_master["has_sleep_log"]]
    fig, ax = plt.subplots(figsize=(8, 5))
    hours = sleep["TotalMinutesAsleep"] / 60
    sns.histplot(hours, bins=24, color=PALETTE["secondary"], ax=ax)
    ax.axvline(7, color=PALETTE["highlight"], linestyle="--", label="7-hour reference line")
    ax.set_title("How much do users sleep on nights they log sleep?\nDistribution of nightly sleep duration")
    ax.set_xlabel("Hours asleep")
    ax.set_ylabel("Number of user-nights")
    ax.legend()
    return _save(fig, "sleep_duration_distribution.png")


def plot_active_vs_sedentary_minutes(user_summary: pd.DataFrame) -> Path:
    data = user_summary.dropna(subset=["avg_active_minutes", "avg_sedentary_minutes"]).sort_values(
        "avg_active_minutes"
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    y_pos = range(len(data))
    ax.barh(y_pos, data["avg_sedentary_minutes"], color=PALETTE["muted"], label="Avg sedentary minutes/day")
    ax.barh(
        y_pos,
        data["avg_active_minutes"],
        left=data["avg_sedentary_minutes"],
        color=PALETTE["primary"],
        label="Avg active minutes/day",
    )
    ax.set_yticks([])
    ax.set_title("How is each user's logged day split between sedentary and active time?")
    ax.set_xlabel("Minutes per day (stacked)")
    ax.set_ylabel("Individual users")
    ax.legend()
    return _save(fig, "active_vs_sedentary_minutes.png")


def plot_steps_vs_calories(user_day_master: pd.DataFrame, corr_result: dict) -> Path:
    worn = user_day_master[~user_day_master["is_non_wear_day"]]
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(
        data=worn,
        x="TotalSteps",
        y="Calories",
        scatter_kws={"alpha": 0.35, "color": PALETTE["primary"], "s": 18},
        line_kws={"color": PALETTE["highlight"]},
        ax=ax,
    )
    ax.set_title(
        "Do more steps mean more calories burned?\n"
        f"Pearson r = {corr_result['pearson_r']}, p {'< 0.001' if corr_result['p_value'] < 0.001 else '= ' + str(round(corr_result['p_value'], 3))}"
    )
    ax.set_xlabel("Total steps per day")
    ax.set_ylabel("Calories burned per day")
    return _save(fig, "steps_vs_calories.png")


def plot_sedentary_vs_sleep(user_day_master: pd.DataFrame, corr_result: dict) -> Path:
    data = user_day_master[user_day_master["has_sleep_log"] & ~user_day_master["is_non_wear_day"]]
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(
        data=data,
        x="SedentaryMinutes",
        y="TotalMinutesAsleep",
        scatter_kws={"alpha": 0.35, "color": PALETTE["secondary"], "s": 18},
        line_kws={"color": PALETTE["highlight"]},
        ax=ax,
    )
    ax.set_title(
        "Is sedentary time on a day associated with sleep that night?\n"
        f"Pearson r = {corr_result['pearson_r']}, p {'< 0.001' if corr_result['p_value'] < 0.001 else '= ' + str(round(corr_result['p_value'], 3))}"
    )
    ax.set_xlabel("Sedentary minutes per day")
    ax.set_ylabel("Minutes asleep that night")
    return _save(fig, "sedentary_vs_sleep.png")


def plot_weekday_weekend_steps(weekday_profile: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [
        PALETTE["accent"] if day in ("Saturday", "Sunday") else PALETTE["primary"]
        for day in weekday_profile["day_of_week"]
    ]
    ax.bar(weekday_profile["day_of_week"], weekday_profile["avg_steps"], color=colors)
    ax.set_title("Which days of the week show the highest activity?\nAverage steps by day of week")
    ax.set_xlabel("Day of week")
    ax.set_ylabel("Average total steps")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, "weekday_weekend_steps.png")


def plot_hourly_activity_profile(hourly_profile: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(9, 5))
    for is_weekend, group in hourly_profile.groupby("is_weekend"):
        label = "Weekend" if is_weekend else "Weekday"
        color = PALETTE["accent"] if is_weekend else PALETTE["primary"]
        ax.plot(group["hour_of_day"], group["avg_steps"], label=label, color=color, linewidth=2)
    ax.set_title("What time of day are users most active?\nAverage steps by hour of day")
    ax.set_xlabel("Hour of day (24h)")
    ax.set_ylabel("Average steps in that hour")
    ax.set_xticks(range(0, 24, 2))
    ax.legend()
    return _save(fig, "hourly_activity_profile.png")


def plot_device_usage_frequency(user_summary: pd.DataFrame) -> Path:
    data = user_summary.sort_values("device_usage_days", ascending=False).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(range(len(data)), data["device_usage_days"], color=PALETTE["primary"])
    ax.axhline(config.STUDY_PERIOD_DAYS, color=PALETTE["muted"], linestyle=":", label="Full 31-day period")
    ax.set_title("How consistently do users log data with their device?\nDays with any recorded activity, per user")
    ax.set_xlabel("Individual users, ranked by usage")
    ax.set_ylabel("Days logged (out of 31)")
    ax.legend()
    return _save(fig, "device_usage_frequency.png")


def plot_user_segments(segmented_users: pd.DataFrame) -> Path:
    data = segmented_users.dropna(subset=["segment", "avg_daily_steps", "avg_sedentary_minutes"])
    order = data.groupby("segment")["avg_daily_steps"].mean().sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=(8, 6))
    for color, segment in zip(SEGMENT_PALETTE, order):
        subset = data[data["segment"] == segment]
        ax.scatter(
            subset["avg_sedentary_minutes"],
            subset["avg_daily_steps"],
            s=90,
            alpha=0.85,
            color=color,
            label=f"{segment} (n={len(subset)})",
        )
    ax.set_title("Are there distinct groups of users by activity behavior?\nUser segments from k-means clustering")
    ax.set_xlabel("Average sedentary minutes per day")
    ax.set_ylabel("Average steps per day")
    ax.legend()
    return _save(fig, "user_segments.png")
