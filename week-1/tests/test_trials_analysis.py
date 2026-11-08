from pathlib import Path

import pandas as pd
import pytest

from src.clean_trials import clean_trials
from src.trials_analysis import cancel_timing, matured_trials, weekly_conversion

PROCESSED = Path("data/processed/trials_clean.csv")
RAW = Path("data/raw/trials.csv")


def _trials() -> pd.DataFrame:
    """Small synthetic table. Latest outcome is 2026-08-20, so the cutoff is 08-06."""
    rows = [
        # trial_id, started_at, outcome, days until outcome
        (1, "2026-08-01", "converted", 14),  # matured, converted
        (2, "2026-08-02", "canceled", 5),  # matured, canceled
        (3, "2026-08-06", "converted", 14),  # exactly on the cutoff: matured
        (4, "2026-08-07", None, None),  # open, started after cutoff
        (5, "2026-08-10", "canceled", 6),  # after cutoff: not matured
    ]
    df = pd.DataFrame(rows, columns=["trial_id", "started_at", "outcome", "days"])
    start = pd.to_datetime(df["started_at"])
    df["started_at"] = start
    df["outcome_at"] = start + pd.to_timedelta(df["days"], unit="D")
    df["ends_at"] = start + pd.Timedelta(days=14)
    return df.drop(columns="days")


def test_matured_excludes_trials_inside_the_window():
    matured = matured_trials(_trials())
    assert sorted(matured["trial_id"]) == [1, 2, 3]


def test_matured_has_no_open_trials():
    assert matured_trials(_trials())["outcome"].notna().all()


def test_matured_rate_not_biased_by_recent_cancels():
    df = _trials()
    closed_only = (df["outcome"].dropna() == "converted").mean()
    matured_rate = matured_trials(df)["converted"].mean()
    assert matured_rate == pytest.approx(2 / 3)
    assert closed_only == pytest.approx(0.5)  # biased low by trial 5


def test_weekly_conversion_counts():
    weekly = weekly_conversion(matured_trials(_trials()))
    assert weekly["trials"].sum() == 3
    assert weekly["converted"].sum() == 2


def test_cancel_timing_counts_whole_days():
    timing = cancel_timing(matured_trials(_trials()))
    assert timing.to_dict() == {5: 1}


def test_clean_trials_flags_open_and_parses_dates():
    raw = _trials().astype({"started_at": str, "ends_at": str, "outcome_at": str})
    raw.loc[raw["outcome"].isna(), "outcome_at"] = None
    clean = clean_trials(raw)
    assert pd.api.types.is_datetime64_any_dtype(clean["started_at"])
    assert clean["is_open"].tolist() == [False, False, False, True, False]


# Golden checks on the real data. Skipped when the data folder is absent.
@pytest.mark.skipif(not PROCESSED.exists(), reason="processed data not present")
class TestRealData:
    @pytest.fixture(scope="class")
    def df(self):
        return pd.read_csv(
            PROCESSED, parse_dates=["started_at", "ends_at", "outcome_at"]
        )

    def test_row_and_open_counts(self, df):
        assert len(df) == 2073
        assert df["is_open"].sum() == 418

    def test_matured_conversion_rate(self, df):
        matured = matured_trials(df)
        assert len(matured) == 1553
        assert matured["converted"].mean() == pytest.approx(0.5332, abs=0.0005)

    def test_closed_only_rate_is_lower_than_matured(self, df):
        closed = df[~df["is_open"]]
        closed_rate = (closed["outcome"] == "converted").mean()
        assert closed_rate == pytest.approx(0.5003, abs=0.0005)
        assert closed_rate < matured_trials(df)["converted"].mean()

    def test_no_cancellations_in_first_four_days(self, df):
        timing = cancel_timing(matured_trials(df))
        assert timing.index.min() >= 4
        assert timing.sum() == 725


@pytest.mark.skipif(not RAW.exists(), reason="raw data not present")
def test_raw_file_unchanged_shape():
    assert pd.read_csv(RAW).shape == (2073, 6)
