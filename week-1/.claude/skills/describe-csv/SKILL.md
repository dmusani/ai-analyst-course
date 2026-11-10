---
name: describe-csv
description: Profile a CSV file (shape, column types, missing values, duplicates, numeric and categorical summaries) and flag data quality issues. Use when the user runs /describe-csv or asks to describe, profile, summarize, or sanity-check a CSV before analysis.
argument-hint: <path/to/file.csv>
---

# describe-csv

Produce a concise profile of a CSV so the user knows what is in it before analysing it.

## Input

`$ARGUMENTS` is the CSV path, relative to the project root (for example `data/raw/example.csv`).

- If empty, list the files in `data/raw/` and ask which one to describe.
- If it is a bare filename (for example `example.csv`), look for exactly one match under `data/` and use it, saying which path you used.
- If the path does not exist, say so and list the CSV files nearby. Do not guess.

## Rules

- Use `poetry run python`, never the system Python.
- Read only. Never modify, move, or overwrite the CSV, and treat `data/raw/` as read-only.
- Use paths relative to the project root, never absolute paths.
- Set `random_state=42` for any sampling.
- Do not install new dependencies. Use pandas, which is already available.
- Do not write files unless the user asks. Print the profile in the reply.

## Steps

1. Load the file with pandas, using `low_memory=False`. If the file has more than about 1M rows, say so and sample with `random_state=42`.
2. Run the profile with `poetry run python -c` or a short heredoc. Collect:
   - **Shape:** rows and columns.
   - **Per column:** dtype, non-null count, missing count and percent, number of unique values.
   - **Numeric columns:** min, max, mean, median, and standard deviation.
   - **Categorical and text columns:** the top 5 values with counts.
   - **Date-like columns:** the min and max, if a column parses as dates.
   - **Duplicates:** the number of fully duplicated rows.
   - **Head:** the first 5 rows.
3. Flag data quality issues:
   - Columns that are more than 5% missing or entirely empty.
   - Constant columns.
   - Numeric columns stored as strings, or dates stored as strings.
   - Negative values in columns that look like amounts or counts.
   - Duplicated rows, and duplicated values in columns that look like IDs.
   - Mixed case or stray whitespace in categorical values.

## Dataset-specific context

This skill works on any CSV, so it holds no notes about particular datasets. If the project's `AGENTS.md` (or a data dictionary) describes the file being profiled, use it to interpret what you find, for example what one row represents or whether a missing value is expected. Say which note you relied on. Do not assume a note applies to a file it does not name.

## Output format

Reply with these sections, using tables for the column details:

1. **Overview:** file, rows, columns, and duplicate rows.
2. **Columns:** one table with dtype, missing %, unique count, and a short note.
3. **Numeric summary:** one table.
4. **Categorical summary:** top values for each categorical column.
5. **Issues found:** a short bulleted list, most serious first. Write "None found" if clean.
6. **Suggested next steps:** one to three cleaning or analysis ideas. Cleaned data goes in `data/processed/`.

Keep it factual. Report what the data shows and do not speculate about causes.
