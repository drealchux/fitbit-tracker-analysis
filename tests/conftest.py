"""Shared pytest fixtures: small synthetic tables shaped like the real data.

Using synthetic data (not the real CSVs) keeps unit tests fast and makes
each test's expected result something a reader can verify by hand.
"""

from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture
def raw_daily_activity() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Id": [1, 1, 2, 2, 3],
            "ActivityDate": pd.to_datetime(
                ["2016-04-12", "2016-04-13", "2016-04-12", "2016-04-13", "2016-04-12"]
            ),
            "TotalSteps": [10000, 0, 5000, 8000, 70000],
            "TotalDistance": [7.0, 0.0, 3.5, 5.5, 40.0],
            "TrackerDistance": [7.0, 0.0, 3.5, 5.5, 40.0],
            "LoggedActivitiesDistance": [0, 0, 0, 0, 0],
            "VeryActiveDistance": [1.0, 0.0, 0.5, 1.0, 5.0],
            "ModeratelyActiveDistance": [0.5, 0.0, 0.2, 0.3, 1.0],
            "LightActiveDistance": [5.5, 0.0, 2.8, 4.2, 34.0],
            "SedentaryActiveDistance": [0, 0, 0, 0, 0],
            "VeryActiveMinutes": [30, 0, 10, 20, 60],
            "FairlyActiveMinutes": [15, 0, 5, 10, 20],
            "LightlyActiveMinutes": [200, 0, 150, 180, 300],
            "SedentaryMinutes": [1195, 1440, 1275, 1230, 1060],
            "Calories": [2200, 1400, 1800, 2000, 2500],
        }
    )


@pytest.fixture
def raw_sleep_day() -> pd.DataFrame:
    """Shaped like the real export: one row per (Id, SleepDay), with
    TotalSleepRecords indicating how many sessions were rolled into that
    row, plus one exact-duplicate row (Id 1, 4/13) as shipped in the raw
    Fitabase data.
    """
    return pd.DataFrame(
        {
            "Id": [1, 1, 1, 2],
            "SleepDay": pd.to_datetime(
                ["2016-04-12", "2016-04-13", "2016-04-13", "2016-04-12"]
            ),
            "TotalSleepRecords": [1, 2, 2, 1],
            "TotalMinutesAsleep": [300, 410, 410, 380],
            "TotalTimeInBed": [320, 430, 430, 400],
        }
    )
