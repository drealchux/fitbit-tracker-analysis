"""Entry point.

Runs Prepare -> Process -> Analyze -> Share and writes every artifact the
project produces:
  - data_processed/*.csv          analysis-ready tables
  - outputs/tables/*.csv          summary and statistical result tables
  - outputs/figures/*.png         charts
  - docs/data_quality_report.md   auto-generated from the cleaning reports

Usage (from the project root, with the virtual environment active):
    python scripts/run_pipeline.py
"""

from __future__ import annotations
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bellabeat import analysis, cleaning, config, data_loading, segmentation, transform, visualization

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("run_pipeline")


def write_csv(df, name: str, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.csv"
    df.to_csv(path, index=False)
    logger.info("Wrote %s (%s rows)", path, len(df))


def main() -> None:
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Prepare: load raw tables
    logger.info("Loading raw data from %s", config.PRIMARY_EXPORT_DIR)
    raw = data_loading.load_all_core()

    # Process: clean each table, collecting quality reports
    quality_reports = []

    daily_activity, rep = cleaning.clean_daily_activity(raw["daily_activity"])
    quality_reports.append(rep)

    sleep_daily, rep = cleaning.clean_sleep_day(raw["sleep_day"])
    quality_reports.append(rep)

    weight_log, rep = cleaning.clean_weight_log(raw["weight_log"])
    quality_reports.append(rep)

    hourly_steps, rep = cleaning.clean_hourly(raw["hourly_steps"], "StepTotal", "hourly_steps")
    quality_reports.append(rep)

    hourly_calories, rep = cleaning.clean_hourly(raw["hourly_calories"], "Calories", "hourly_calories")
    quality_reports.append(rep)

    hourly_intensities, rep = cleaning.clean_hourly(
        raw["hourly_intensities"], "TotalIntensity", "hourly_intensities"
    )
    quality_reports.append(rep)

    daily_activity = transform.add_activity_derived_fields(daily_activity)
    user_day_master = transform.build_user_day_master(daily_activity, sleep_daily)
    user_summary = transform.build_user_summary(user_day_master)
    hourly_usage = transform.build_hourly_usage(hourly_steps, hourly_calories, hourly_intensities)

    write_csv(user_day_master, "user_day_master", config.PROCESSED_DIR)
    write_csv(user_summary, "user_summary", config.PROCESSED_DIR)
    write_csv(hourly_usage, "hourly_usage", config.PROCESSED_DIR)

    # Analyze: descriptive stats, correlation / group tests, segmentation
    worn_days = user_day_master[~user_day_master["is_non_wear_day"]]

    activity_desc = analysis.describe_numeric(
        worn_days,
        ["TotalSteps", "Calories", "SedentaryMinutes", "total_active_minutes", "TotalDistance"],
    )
    write_csv(activity_desc, "descriptive_activity_stats", config.TABLES_DIR)

    sleep_desc = analysis.describe_numeric(
        user_day_master[user_day_master["has_sleep_log"]],
        ["TotalMinutesAsleep", "TotalTimeInBed"],
    )
    write_csv(sleep_desc, "descriptive_sleep_stats", config.TABLES_DIR)

    corr_steps_calories = analysis.correlation_test(
        worn_days, "TotalSteps", "Calories", "Steps vs. calories burned"
    )
    corr_steps_sleep = analysis.correlation_test(
        user_day_master[user_day_master["has_sleep_log"] & ~user_day_master["is_non_wear_day"]],
        "TotalSteps",
        "TotalMinutesAsleep",
        "Steps vs. sleep duration",
    )
    corr_sedentary_sleep = analysis.correlation_test(
        user_day_master[user_day_master["has_sleep_log"] & ~user_day_master["is_non_wear_day"]],
        "SedentaryMinutes",
        "TotalMinutesAsleep",
        "Sedentary minutes vs. sleep duration",
    )
    corr_distance_calories = analysis.correlation_test(
        worn_days, "TotalDistance", "Calories", "Distance vs. calories burned"
    )

    weekday_weekend_steps = analysis.weekday_weekend_test(
        worn_days, "TotalSteps", "Weekday vs. weekend steps"
    )
    weekday_weekend_sedentary = analysis.weekday_weekend_test(
        worn_days, "SedentaryMinutes", "Weekday vs. weekend sedentary minutes"
    )

    stat_results = [
        corr_steps_calories,
        corr_steps_sleep,
        corr_sedentary_sleep,
        corr_distance_calories,
        weekday_weekend_steps,
        weekday_weekend_sedentary,
    ]
    with open(config.TABLES_DIR / "statistical_test_results.json", "w") as f:
        json.dump(stat_results, f, indent=2, default=str)
    logger.info("Wrote statistical_test_results.json")

    usage_tiers = analysis.device_usage_frequency(user_summary)
    write_csv(usage_tiers, "device_usage_tiers", config.TABLES_DIR)

    activity_tier_days = analysis.activity_tier_distribution(worn_days)
    write_csv(activity_tier_days, "activity_tier_distribution_days", config.TABLES_DIR)

    activity_tier_users = analysis.activity_tier_distribution(user_summary)
    write_csv(activity_tier_users, "activity_tier_distribution_users", config.TABLES_DIR)

    hourly_profile = analysis.hourly_activity_profile(hourly_usage)
    write_csv(hourly_profile, "hourly_activity_profile", config.TABLES_DIR)

    weekday_profile = analysis.weekday_activity_profile(worn_days)
    write_csv(weekday_profile, "weekday_activity_profile", config.TABLES_DIR)

    segmented_users, segmentation_report = segmentation.segment_users(user_summary)
    write_csv(segmented_users, "user_segments", config.TABLES_DIR)
    with open(config.TABLES_DIR / "segmentation_report.json", "w") as f:
        json.dump(segmentation_report, f, indent=2, default=str)
    logger.info("Wrote segmentation_report.json")


    # Share: charts
    visualization.plot_daily_steps_distribution(user_day_master)
    visualization.plot_sleep_duration_distribution(user_day_master)
    visualization.plot_active_vs_sedentary_minutes(user_summary)
    visualization.plot_steps_vs_calories(user_day_master, corr_steps_calories)
    visualization.plot_sedentary_vs_sleep(user_day_master, corr_sedentary_sleep)
    visualization.plot_weekday_weekend_steps(weekday_profile)
    visualization.plot_hourly_activity_profile(hourly_profile)
    visualization.plot_device_usage_frequency(user_summary)
    visualization.plot_user_segments(segmented_users)
    visualization.plot_activity_tier_distribution(activity_tier_days)
    logger.info("Wrote 10 figures to %s", config.FIGURES_DIR)

    # Data quality report (auto-generated, feeds docs/data_quality_report.md)
    with open(config.TABLES_DIR / "data_quality_reports.json", "w") as f:
        json.dump(quality_reports, f, indent=2, default=str)
    logger.info("Wrote data_quality_reports.json")

    logger.info("Pipeline complete.")


if __name__ == "__main__":
    main()
