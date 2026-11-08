"""Clean data/raw/trials.csv and write the result to data/processed/."""

from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/trials.csv")
PROCESSED_PATH = Path("data/processed/trials_clean.csv")

DATE_COLUMNS = ["started_at", "ends_at", "outcome_at"]


def clean_trials(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the raw trials table.

    - started_at, ends_at, outcome_at parsed to datetime.
    - is_open flag added: True when the trial has no outcome yet. Open trials
      are still running, so exclude them from conversion rates.
    - outcome and outcome_at left null for open trials (not an error).
    """
    out = df.copy()
    for col in DATE_COLUMNS:
        out[col] = pd.to_datetime(out[col])
    out["is_open"] = out["outcome"].isna()
    return out


def main() -> None:
    raw = pd.read_csv(RAW_PATH)
    clean = clean_trials(raw)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(PROCESSED_PATH, index=False)
    print(f"Wrote {len(clean)} rows to {PROCESSED_PATH}")


if __name__ == "__main__":
    main()
