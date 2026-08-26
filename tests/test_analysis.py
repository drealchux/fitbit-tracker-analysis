"""Tests for src/bellabeat/analysis.py."""

from __future__ import annotations
import numpy as np
import pandas as pd
from bellabeat import analysis

class TestDescribeNumeric:
    def test_reports_mean_median_and_skew(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 100]})
        result = analysis.describe_numeric(df, ["x"])
        row = result.iloc[0]
        assert row["mean"] == 22.0
        assert row["median"] == 3.0
        assert row["skew_mean_minus_median_pct"] > 0  # right-skewed: mean pulled above median


class TestCorrelationTest:
    def test_perfect_positive_correlation(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]})
        result = analysis.correlation_test(df, "x", "y", "perfect linear")
        assert result["pearson_r"] == 1.0
        assert result["significant_at_0.05"] is True

    def test_no_correlation_is_not_significant(self):
        rng = np.random.default_rng(0)
        df = pd.DataFrame({"x": rng.normal(size=200), "y": rng.normal(size=200)})
        result = analysis.correlation_test(df, "x", "y", "random noise")
        assert abs(result["pearson_r"]) < 0.2

    def test_drops_rows_with_missing_values_before_testing(self):
        df = pd.DataFrame({"x": [1, 2, np.nan, 4], "y": [1, 2, 3, 4]})
        result = analysis.correlation_test(df, "x", "y", "with nan")
        assert result["n"] == 3


class TestWeekdayWeekendTest:
    def test_detects_a_real_difference(self):
        rng = np.random.default_rng(1)
        df = pd.DataFrame(
            {
                "is_weekend": [False] * 50 + [True] * 50,
                "value": np.concatenate(
                    [rng.normal(100, 5, 50), rng.normal(200, 5, 50)]
                ),
            }
        )
        result = analysis.weekday_weekend_test(df, "value", "synthetic gap")
        assert 95 < result["weekday_mean"] < 105
        assert 195 < result["weekend_mean"] < 205
        assert result["significant_at_0.05"] is True


class TestActivityTierDistribution:
    def test_counts_and_percentages_by_tier(self):
        df = pd.DataFrame(
            {
                "activity_tier": pd.Categorical(
                    ["Sedentary (<5,000)", "Sedentary (<5,000)", "Highly active (12,500+)", "Active (10,000-12,499)"],
                    categories=analysis.config.STEP_TIER_LABELS,
                )
            }
        )
        result = analysis.activity_tier_distribution(df).set_index("activity_tier")
        assert result.loc["Sedentary (<5,000)", "n"] == 2
        assert result.loc["Sedentary (<5,000)", "pct"] == 50.0
        assert result.loc["Low active (5,000-7,499)", "n"] == 0
        assert result["n"].sum() == 4


class TestDeviceUsageFrequency:
    def test_buckets_users_by_days_logged(self):
        df = pd.DataFrame({"Id": [1, 2, 3, 4], "device_usage_days": [5, 15, 25, 31]})
        result = analysis.device_usage_frequency(df)
        tiers = result.set_index("Id")["usage_frequency_tier"]
        assert tiers[1] == "Low use (<=10 days)"
        assert tiers[4] == "Near-daily use (28-31 days)"
