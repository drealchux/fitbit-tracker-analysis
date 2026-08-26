"""Central configuration: paths and analysis constants.

Keeping all paths and thresholds in one place avoids magic strings and
magic numbers scattered across the pipeline, and makes the project
relocatable (only this file needs to change if the data folder moves).
"""

from __future__ import annotations
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

# The dataset ships as two Fitabase exports covering overlapping periods.
# The 4/12/2016-5/12/2016 export is the primary source: it is a complete
# 31-day period and is the only export that includes the daily-aggregate
# files (dailyCalories, dailySteps, dailyIntensities, sleepDay). The
# 3/12/2016-4/11/2016 export overlaps the first day of the primary export,
# has a different user roster (35 vs. 33 users), and lacks the daily sleep
# and daily-aggregate tables, so it is excluded from the analysis to avoid
# double-counting user-days and inconsistent granularity. This decision is
# documented in docs/data_quality_report.md.
PRIMARY_EXPORT_DIR = (
    DATA_DIR
    / "mturkfitbit_export_4.12.16-5.12.16"
    / "Fitabase Data 4.12.16-5.12.16"
)

EXCLUDED_EXPORT_DIR = (
    DATA_DIR
    / "mturkfitbit_export_3.12.16-4.11.16"
    / "Fitabase Data 3.12.16-4.11.16"
)

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
TABLES_DIR = OUTPUTS_DIR / "tables"
PROCESSED_DIR = PROJECT_ROOT / "data_processed"
DOCS_DIR = PROJECT_ROOT / "docs"

RAW_FILES = {
    "daily_activity": PRIMARY_EXPORT_DIR / "dailyActivity_merged.csv",
    "daily_calories": PRIMARY_EXPORT_DIR / "dailyCalories_merged.csv",
    "daily_intensities": PRIMARY_EXPORT_DIR / "dailyIntensities_merged.csv",
    "daily_steps": PRIMARY_EXPORT_DIR / "dailySteps_merged.csv",
    "sleep_day": PRIMARY_EXPORT_DIR / "sleepDay_merged.csv",
    "hourly_steps": PRIMARY_EXPORT_DIR / "hourlySteps_merged.csv",
    "hourly_calories": PRIMARY_EXPORT_DIR / "hourlyCalories_merged.csv",
    "hourly_intensities": PRIMARY_EXPORT_DIR / "hourlyIntensities_merged.csv",
    "weight_log": PRIMARY_EXPORT_DIR / "weightLogInfo_merged.csv",
    "heartrate": PRIMARY_EXPORT_DIR / "heartrate_seconds_merged.csv",
}

# Analysis constants

# A day is considered "worn" if the device recorded any steps or any
# non-sedentary minutes. A total of 0 steps and 1440 sedentary minutes is
# treated as a non-wear day rather than a genuinely inactive day, since it
# is far more likely the device was not worn (documented in the CDC/Fitabase
# literature on this dataset).
NON_WEAR_STEP_THRESHOLD = 0
MINUTES_PER_DAY = 1440

# CDC / WHO reference: 10,000 steps/day is a commonly cited public target,
# though not a formal clinical guideline. Used here only to build
# descriptive activity tiers, not as a medical claim.
STEP_TIER_BINS = [-1, 5000, 7500, 10000, 12500, float("inf")]
STEP_TIER_LABELS = [
    "Sedentary (<5,000)",
    "Low active (5,000-7,499)",
    "Somewhat active (7,500-9,999)",
    "Active (10,000-12,499)",
    "Highly active (12,500+)",
]

# Plausible physiological ranges used for outlier / impossible-value checks.
MAX_PLAUSIBLE_STEPS_PER_DAY = 50000
MAX_PLAUSIBLE_CALORIES_PER_DAY = 6000
MIN_PLAUSIBLE_CALORIES_PER_DAY = 500
MAX_PLAUSIBLE_SLEEP_MINUTES = 900  # 15 hours
MIN_PLAUSIBLE_SLEEP_MINUTES = 30

# Minimum number of logged days for a user to be considered "engaged"
# enough to include in device-usage-frequency comparisons. 31 calendar
# days are covered by the primary export.
STUDY_PERIOD_DAYS = 31

RANDOM_SEED = 42

FIGURE_DPI = 150
