# AGENTS.md
 
## Project overview
Analysis of customer orders for the growth team. Raw data is in `data/`, notebooks in `notebooks/`, and reusable code in `src/`.
 
## Commands
- Install dependencies: `poetry install`
- Run Python with `poetry run python`, never the system Python.
- Run tests: `poetry run pytest -q`
- Lint and format: `poetry run ruff check --fix` and `poetry run ruff format`
 
## Working with data
- Treat `data/raw/` as read-only. Write cleaned data to `data/processed/`.
- `orders.csv` has one row per order line, not per order. Count orders with `order_id`. `Total` refers to the invoice amount in US Dollars
- Never commit data files or anything in `outputs/`.
 
## Conventions
- Put reusable logic in `src/`. Notebooks import from it instead of redefining it.
- Use paths relative to the project root, never absolute paths.
- Set `random_state=42` wherever randomness is involved.
 
## Ask first
- Before installing a new dependency.
- Before deleting or overwriting any data file.
- Never write credentials into code. Read them from environment variables.