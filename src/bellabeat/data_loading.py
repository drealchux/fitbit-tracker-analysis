"""Raw CSV loading for the Bellabeat / Fitabase dataset.

Every function here does the minimum necessary to get a raw CSV into a
DataFrame with correctly typed columns. No cleaning, filtering, or
business logic happens in this module; that belongs in cleaning.py and
transform.py. Keeping loading separate makes it easy to reason about the
data quality report, which needs to inspect the data exactly as-shipped.
"""

from __future__ import annotations
import logging
from pathlib import Path
import pandas as pd
from . import config
logger = logging.getLogger(__name__)


def _read_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Expected raw data file not found: {path}")
    df = pd.read_csv(path)
    logger.info("Loaded %s rows from %s", len(df), path.name)
    return df


def load_daily_activity() -> pd.DataFrame:
    """dailyActivity_merged.csv: one row per user per day, full activity summary."""
    df = _read_csv(config.RAW_FILES["daily_activity"])
    df["ActivityDate"] = pd.to_datetime(df["ActivityDate"], format="%m/%d/%Y")
    return df


def load_sleep_day() -> pd.DataFrame:
    """sleepDay_merged.csv: one row per user per sleep session logged."""
    df = _read_csv(config.RAW_FILES["sleep_day"])
    df["SleepDay"] = pd.to_datetime(df["SleepDay"], format="%m/%d/%Y %I:%M:%S %p")
    return df


def load_hourly_steps() -> pd.DataFrame:
    df = _read_csv(config.RAW_FILES["hourly_steps"])
    df["ActivityHour"] = pd.to_datetime(df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    return df


def load_hourly_calories() -> pd.DataFrame:
    df = _read_csv(config.RAW_FILES["hourly_calories"])
    df["ActivityHour"] = pd.to_datetime(df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    return df


def load_hourly_intensities() -> pd.DataFrame:
    df = _read_csv(config.RAW_FILES["hourly_intensities"])
    df["ActivityHour"] = pd.to_datetime(df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    return df


def load_weight_log() -> pd.DataFrame:
    df = _read_csv(config.RAW_FILES["weight_log"])
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y %I:%M:%S %p")
    return df


def load_heartrate() -> pd.DataFrame:
    """heartrate_seconds_merged.csv: very large (~2.5M rows), second-level readings."""
    df = _read_csv(config.RAW_FILES["heartrate"])
    df["Time"] = pd.to_datetime(df["Time"], format="%m/%d/%Y %I:%M:%S %p")
    return df


def load_all_core() -> dict[str, pd.DataFrame]:
    """Load the tables needed for the daily activity / sleep analysis.

    Excludes heartrate (very large, only used for supplementary summary
    statistics) so that the default pipeline run stays fast.
    """
    return {
        "daily_activity": load_daily_activity(),
        "sleep_day": load_sleep_day(),
        "hourly_steps": load_hourly_steps(),
        "hourly_calories": load_hourly_calories(),
        "hourly_intensities": load_hourly_intensities(),
        "weight_log": load_weight_log(),
    }
