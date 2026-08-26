"""Tests for src/bellabeat/segmentation.py."""

from __future__ import annotations

import numpy as np
import pandas as pd

from bellabeat import segmentation


def _synthetic_user_summary(n_low: int = 8, n_high: int = 8) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    low = pd.DataFrame(
        {
            "avg_daily_steps": rng.normal(3000, 300, n_low),
            "avg_sedentary_minutes": rng.normal(1200, 50, n_low),
            "avg_active_minutes": rng.normal(100, 15, n_low),
            "avg_daily_calories": rng.normal(1800, 100, n_low),
            "device_usage_days": rng.integers(20, 31, n_low),
        }
    )
    high = pd.DataFrame(
        {
            "avg_daily_steps": rng.normal(13000, 300, n_high),
            "avg_sedentary_minutes": rng.normal(700, 50, n_high),
            "avg_active_minutes": rng.normal(300, 15, n_high),
            "avg_daily_calories": rng.normal(2600, 100, n_high),
            "device_usage_days": rng.integers(20, 31, n_high),
        }
    )
    combined = pd.concat([low, high], ignore_index=True)
    combined["Id"] = range(1, len(combined) + 1)
    return combined


class TestSegmentUsers:
    def test_finds_two_well_separated_groups(self):
        summary = _synthetic_user_summary()
        result, report = segmentation.segment_users(summary)
        assert result["segment"].notna().all()
        assert set(result["segment"].unique()) == {"Low activity", "High activity"}

    def test_every_user_gets_a_segment_label(self):
        summary = _synthetic_user_summary()
        result, _ = segmentation.segment_users(summary)
        assert len(result) == len(summary)
        assert result["segment"].isna().sum() == 0

    def test_label_direction_matches_step_count(self):
        summary = _synthetic_user_summary()
        result, report = segmentation.segment_users(summary)
        profile = report["segment_profile_means"]
        assert profile["High activity"]["avg_daily_steps"] > profile["Low activity"]["avg_daily_steps"]
