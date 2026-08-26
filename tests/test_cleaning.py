"""Tests for src/bellabeat/cleaning.py."""

from __future__ import annotations

from bellabeat import cleaning


class TestCleanDailyActivity:
    def test_flags_non_wear_days(self, raw_daily_activity):
        cleaned, report = cleaning.clean_daily_activity(raw_daily_activity)
        non_wear_rows = cleaned[cleaned["is_non_wear_day"]]
        assert len(non_wear_rows) == 1
        assert non_wear_rows.iloc[0]["Id"] == 1
        assert report["non_wear_days_flagged"] == 1

    def test_flags_implausible_steps_but_does_not_drop_rows(self, raw_daily_activity):
        cleaned, report = cleaning.clean_daily_activity(raw_daily_activity)
        # 70,000 steps exceeds MAX_PLAUSIBLE_STEPS_PER_DAY; flagged in the
        # report but the row is kept (not fabricated evidence of fraud,
        # just an outlier worth flagging for analyst awareness).
        assert report["rows_with_implausible_steps"] == 1
        assert report["output_rows"] == len(raw_daily_activity)

    def test_drops_exact_duplicate_rows(self, raw_daily_activity):
        with_dupe = raw_daily_activity.copy()
        with_dupe = pd_concat_first_row(with_dupe)
        cleaned, report = cleaning.clean_daily_activity(with_dupe)
        assert report["exact_duplicate_rows_dropped"] == 1
        assert len(cleaned) == len(raw_daily_activity)

    def test_reports_unique_users_and_date_range(self, raw_daily_activity):
        _, report = cleaning.clean_daily_activity(raw_daily_activity)
        assert report["unique_users"] == 3
        assert report["date_min"] == "2016-04-12"
        assert report["date_max"] == "2016-04-13"


class TestCleanSleepDay:
    def test_drops_exact_duplicate_row(self, raw_sleep_day):
        cleaned, report = cleaning.clean_sleep_day(raw_sleep_day)
        assert report["exact_duplicate_rows_dropped"] == 1
        user1_day2 = cleaned[(cleaned["Id"] == 1) & (cleaned["SleepDay"] == "2016-04-13")]
        assert len(user1_day2) == 1
        assert user1_day2.iloc[0]["TotalMinutesAsleep"] == 410

    def test_output_has_one_row_per_user_day(self, raw_sleep_day):
        cleaned, _ = cleaning.clean_sleep_day(raw_sleep_day)
        assert not cleaned.duplicated(subset=["Id", "SleepDay"]).any()
        assert len(cleaned) == 3  # (1, 4/12), (1, 4/13), (2, 4/12)

    def test_reports_multi_session_rows(self, raw_sleep_day):
        _, report = cleaning.clean_sleep_day(raw_sleep_day)
        # Id 1 / 4-13 has TotalSleepRecords == 2 (a nap plus overnight sleep
        # already rolled into that one row). Two identical copies of that
        # row ship in the fixture; one is dropped as an exact duplicate
        # before this count is taken, leaving one multi-session row.
        assert report["multi_session_day_rows_before_aggregation"] == 1


def pd_concat_first_row(df):
    import pandas as pd

    return pd.concat([df, df.iloc[[0]]], ignore_index=True)
