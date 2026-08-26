"""Tests for src/bellabeat/transform.py."""

from __future__ import annotations

from bellabeat import cleaning, transform


class TestAddActivityDerivedFields:
    def test_total_active_minutes_sums_three_intensity_levels(self, raw_daily_activity):
        cleaned, _ = cleaning.clean_daily_activity(raw_daily_activity)
        result = transform.add_activity_derived_fields(cleaned)
        row = result[result["Id"] == 1].iloc[0]
        assert row["total_active_minutes"] == 30 + 15 + 200

    def test_sedentary_share_pct_is_between_0_and_100(self, raw_daily_activity):
        cleaned, _ = cleaning.clean_daily_activity(raw_daily_activity)
        result = transform.add_activity_derived_fields(cleaned)
        assert (result["sedentary_share_pct"] >= 0).all()
        assert (result["sedentary_share_pct"] <= 100).all()


class TestBuildUserDayMaster:
    def test_left_join_keeps_activity_rows_without_sleep(self, raw_daily_activity, raw_sleep_day):
        activity, _ = cleaning.clean_daily_activity(raw_daily_activity)
        activity = transform.add_activity_derived_fields(activity)
        sleep, _ = cleaning.clean_sleep_day(raw_sleep_day)
        merged = transform.build_user_day_master(activity, sleep)
        # Id 3 has no sleep log at all in the fixture.
        id3_row = merged[merged["Id"] == 3].iloc[0]
        assert id3_row["has_sleep_log"] == False  # noqa: E712
        assert len(merged) == len(activity)

    def test_matches_sleep_to_correct_user_and_date(self, raw_daily_activity, raw_sleep_day):
        activity, _ = cleaning.clean_daily_activity(raw_daily_activity)
        activity = transform.add_activity_derived_fields(activity)
        sleep, _ = cleaning.clean_sleep_day(raw_sleep_day)
        merged = transform.build_user_day_master(activity, sleep)
        row = merged[(merged["Id"] == 1) & (merged["ActivityDate"] == "2016-04-12")].iloc[0]
        assert row["TotalMinutesAsleep"] == 300


class TestBuildUserSummary:
    def test_non_wear_days_excluded_from_activity_averages(self, raw_daily_activity, raw_sleep_day):
        activity, _ = cleaning.clean_daily_activity(raw_daily_activity)
        activity = transform.add_activity_derived_fields(activity)
        sleep, _ = cleaning.clean_sleep_day(raw_sleep_day)
        master = transform.build_user_day_master(activity, sleep)
        summary = transform.build_user_summary(master)
        # Id 1 has one worn day (10,000 steps) and one non-wear day (0 steps).
        # The average should reflect only the worn day, not (10000 + 0) / 2.
        id1 = summary[summary["Id"] == 1].iloc[0]
        assert id1["avg_daily_steps"] == 10000
        assert id1["active_days"] == 1

    def test_device_usage_days_counts_all_recorded_days_including_non_wear(
        self, raw_daily_activity, raw_sleep_day
    ):
        activity, _ = cleaning.clean_daily_activity(raw_daily_activity)
        activity = transform.add_activity_derived_fields(activity)
        sleep, _ = cleaning.clean_sleep_day(raw_sleep_day)
        master = transform.build_user_day_master(activity, sleep)
        summary = transform.build_user_summary(master)
        id1 = summary[summary["Id"] == 1].iloc[0]
        assert id1["device_usage_days"] == 2
