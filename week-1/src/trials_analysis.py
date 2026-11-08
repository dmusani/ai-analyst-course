"""Conversion analysis helpers for the cleaned trials table."""

import pandas as pd

TRIAL_DAYS = 14


def matured_trials(df: pd.DataFrame) -> pd.DataFrame:
    """Return trials that have had a full 14 days to resolve.

    Open trials are excluded from conversion rates, but dropping only open
    rows biases recent weeks low: cancels happen early and conversions only
    land on day 14. Keeping trials that started at least 14 days before the
    latest recorded outcome means every row here has a final outcome.
    """
    snapshot = df["outcome_at"].max()
    cutoff = snapshot - pd.Timedelta(days=TRIAL_DAYS)
    out = df[df["started_at"] <= cutoff].copy()
    out["converted"] = (out["outcome"] == "converted").astype(int)
    return out


def weekly_conversion(matured: pd.DataFrame) -> pd.DataFrame:
    """Conversion rate by start week (weeks start on Monday)."""
    week = matured["started_at"].dt.to_period("W-SUN").dt.start_time
    out = matured.groupby(week).agg(
        trials=("converted", "size"),
        converted=("converted", "sum"),
        rate=("converted", "mean"),
    )
    out.index.name = "week_start"
    return out.reset_index()


def cancel_timing(matured: pd.DataFrame) -> pd.Series:
    """Number of canceled trials by whole day since the trial started."""
    canceled = matured[matured["outcome"] == "canceled"]
    days = (canceled["outcome_at"] - canceled["started_at"]).dt.days
    return days.value_counts().sort_index()
