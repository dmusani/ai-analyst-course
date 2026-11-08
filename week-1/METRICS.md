# METRICS.md

Metric definitions for `data/raw/trials.csv`. **Status: approved by the growth team** (confirmed by the repo owner on 2026-11-08). Change a definition only with the growth team's agreement, and update this note when you do.

## Trial conversion rate

- **Meaning:** Share of free trials that end in a paid conversion.
- **Formula:** `converted / (converted + canceled)`
- **Population:** Matured trials only, meaning trials that started at least 14 days before the latest `outcome_at` in the data. Every matured trial has a final outcome.
- **Why not "all closed trials":** Cancellations happen on days 4-13, but conversions only land on day 14 (`outcome_at == ends_at`). Using every closed trial makes recent weeks look worse than they are, because their conversions have not happened yet.
- **Current value:** 53.3% (1,553 matured trials, snapshot 2026-09-24). Closed-only gives 50.0%, which is biased low.
- **Code:** `src/trials_analysis.py` (`matured_trials`).

## Open trial

- **Meaning:** A trial that has no outcome yet. `outcome` and `outcome_at` are both null.
- **Handling:** Never counted as a conversion or a cancellation. Flagged with `is_open` in `data/processed/trials_clean.csv`.

## Weekly conversion rate (start-week cohort)

- **Meaning:** Conversion rate of matured trials grouped by the week they started (weeks begin on Monday).
- **Caveat:** The first week (2026-07-27) is partial, with trials from Aug 1-2 only (n=88). Do not read it as a trend.
- **Code:** `src/trials_analysis.py` (`weekly_conversion`).

## Time to cancel

- **Meaning:** Whole days from `started_at` to `outcome_at` for canceled trials.
- **Current shape:** No cancellations in days 0-3. About 64-83 per day across days 4-13.
- **Code:** `src/trials_analysis.py` (`cancel_timing`).

## Notes

- Timestamps in the raw file are strings. Parse them before use (`src/clean_trials.py` does this).
- The trial length is 14 days for every trial in the current data.
- `Total` and `orders.csv` metrics are not covered here. Add them if that file comes back.
