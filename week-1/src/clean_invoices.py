"""Clean data/raw/invoices.csv and write the result to data/processed/."""

from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/invoices.csv")
PROCESSED_PATH = Path("data/processed/invoices_clean.csv")


def clean_invoices(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the raw invoices table.

    - InvoiceDate parsed to datetime (all raw values are midnight, so date only).
    - String columns stripped of leading/trailing whitespace (e.g. 'Edinburgh ').
    - BillingState left null where missing: it does not apply to every country.
    """
    out = df.copy()
    out["InvoiceDate"] = pd.to_datetime(out["InvoiceDate"]).dt.normalize()
    for col in out.select_dtypes(include="object").columns:
        out[col] = out[col].str.strip()
    return out


def main() -> None:
    # Read postal codes as strings so values like '0171' keep their zeros.
    raw = pd.read_csv(RAW_PATH, dtype={"BillingPostalCode": str})
    clean = clean_invoices(raw)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(PROCESSED_PATH, index=False)
    print(f"Wrote {len(clean)} rows to {PROCESSED_PATH}")


if __name__ == "__main__":
    main()
