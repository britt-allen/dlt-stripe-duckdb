# dlt-stripe-duckdb

AI was used in the creation of this pipeline and even this readme. I wrote about my learning project using Claude Plan Mode [here](https://medium.com/@britt-allen/learning-dlt-stripe-and-duckdb-with-claude-plan-mode-a921c5ba9036?sharedUserId=britt-allen) which inspired this repo. If you use this repo and run into issues and feel so compelled to submit a PR you are welcome to. This is not meant to be perfect, be kind.

Loads fake `Customer` and `Charge` data from Stripe into DuckDB, using dlt's `stripe_analytics` verified source.

## Prerequisites (Linux and macOS)

1. Run the following command to install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Run the following command to install the DuckDB CLI: `curl https://install.duckdb.org | sh`
3. A Stripe account with a test-mode secret key (`sk_test_...`)

## Setup

1. Install dependencies into `.venv`, per `uv.lock`

```bash
uv sync
```

2. Create `.dlt/secrets.toml`

```toml
[sources.stripe_analytics]
stripe_secret_key = "sk_test_..."
```

3. Create the fake data

```bash
export STRIPE_SECRET_KEY=sk_test_...
bash scripts/seed_stripe.sh
```

Creates 100 fake customers, each with one charge, directly via Stripe's API.

## Load data

1. Run

```bash
uv run python stripe_analytics_pipeline.py
```

Loads `Customer` and `Charge` into `stripe_analytics.duckdb`, schema `stripe_updated`.

## Inspect the data

1. Run

```bash
duckdb -ui stripe_analytics.duckdb
```

2. List all tables

```
SHOW ALL TABLES;
```

3. Query the `customer` table

```SQL
SELECT * FROM stripe_updated.customer
```

## Notes

- Both resources use `write_disposition="replace"` — reruns replace existing rows, they don't duplicate them.
- `stripe_analytics/__init__.py` pins `stripe.api_version` to `2026-07-29.dahlia`. Stripe deprecates old versions periodically, so this may need bumping later.

### Files in this repo

| File | How / why generated | Must pre-exist, or auto-created? |
|---|---|---|
| `.dlt/config.toml` | `dlt init` scaffold — non-secret runtime config | Must pre-exist — only `dlt init` creates it |
| `.dlt/.sources` | `dlt init` scaffold — tracks hashes of the original verified-source template files, so `dlt init` can tell edited files from untouched ones | Must pre-exist — without it, rerunning `dlt init` could overwrite the edits in `stripe_analytics_pipeline.py` / `stripe_analytics/__init__.py` |
| `.gitignore` | `uv init` default, edited to add `.dlt/secrets.toml` + `*.duckdb` | Must pre-exist |
| `.python-version` | `uv init` — pins Python 3.13 | Must pre-exist |
| `pyproject.toml` | `uv init`, deps added via `uv add` (`dlt[duckdb]`, `stripe`) | Must pre-exist — `uv sync` reads it, doesn't create it |
| `README.md` | Instructions for this repo (creation was assisted by AI) | Must pre-exist |
| `scripts/seed_stripe.sh` | Seeds fake Stripe data (creation was assisted by AI) | Must pre-exist |
| `src/dlt_stripe_duckdb/__init__.py` | `uv init` default boilerplate, unused | Must pre-exist — likely needed for `uv sync` to build the local package (not independently confirmed) |
| `stripe_analytics_pipeline.py` | `dlt init stripe_analytics duckdb` scaffold, edited (endpoints scoped to Customer/Charge) | Must pre-exist |
| `stripe_analytics/__init__.py` | `dlt init` verified-source code, edited (api_version fix) | Must pre-exist |
| `stripe_analytics/helpers.py` | `dlt init` verified-source code, untouched | Must pre-exist |
| `stripe_analytics/README.md` | `dlt init` verified-source's own generic docs, untouched | Must pre-exist |
| `stripe_analytics/settings.py` | `dlt init` verified-source code, untouched (`ENDPOINTS` constants) | Must pre-exist |
| `uv.lock` | `uv` auto-generated lockfile | Auto-created by `uv sync` if missing (committing it pins exact versions) |
