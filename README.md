# TollGate

Scheduled ETL pipeline with data-quality gates — no record reaches the analytics
tables until it passes.

Weather data for 10 Indian cities is pulled hourly from the Open-Meteo archive API,
landed in an immutable raw table, aggregated into daily per-city statistics, and
validated before it is allowed into the analytics layer. A failing check aborts the
run with a non-zero exit code and records the reason.

## Architecture

```
Open-Meteo API
      │
      ▼
  extract.py ──────► raw_weather          (immutable landing zone, append-only)
                          │
                          ▼
                    transform.py          (daily aggregates, computed in SQL)
                          │
                          ▼
                     checks.py            ◄── QUALITY GATE
                          │
                    pass ──┴── fail ──► run_log(status='failed'), exit 1
                          │
                          ▼
                     load.py ──────► daily_city_weather   (analytics layer)
```

Every run — success or failure — writes a row to `run_log`.

## Why checks run before the load

The gate sits between the transform and the analytics table, not after it. If a
check fails, `daily_city_weather` is never written to, so downstream consumers
never see partial or wrong data. The alternative — load first, validate after —
means bad data is already visible while you decide what to do about it.

The raw layer is deliberately *outside* the gate. `raw_weather` is an audit trail
of what the API actually returned, including data that later failed validation.
It is never mutated or deleted from; reprocessing rebuilds the modelled table from
raw rather than re-fetching.

## Data model

| Table | Grain | Purpose |
|---|---|---|
| `raw_weather` | one row per city per hour | immutable landing zone |
| `daily_city_weather` | one row per city per day | modelled analytics output |
| `run_log` | one row per pipeline execution | run history and failure reasons |

`raw_weather` has a composite primary key on `(city, ts)` and loads with
`ON CONFLICT DO NOTHING` — re-running a date is a no-op. `daily_city_weather`
has a composite key on `(city, day)` and loads with `ON CONFLICT DO UPDATE`,
because a derived aggregate should be recomputed rather than skipped.

## Quality checks

1. Exactly 24 readings per city per day
2. No nulls in `city` or `day`
3. All temperature values within −50 °C to 60 °C
4. No duplicate `(city, day)` pairs

Checks are a declarative list; all of them run before any failure is raised, so a
single run reports every problem it found rather than only the first.

A fifth check from the original design — comparing daily row counts against a
trailing average — is not implemented in v1. It requires several days of history
to be meaningful, and shipping a check that can never fire on the available data
would be worse than leaving it out.

## Running locally

```bash
cp .env.example .env        # fill in the values
docker compose up -d
psql -f sql/schema.sql      # or run it through the container
pip install -r requirements.txt
python -m tollgate.pipeline 2026-08-18
```

Postgres publishes on host port **5433**.

## Scheduling

A GitHub Actions workflow runs the pipeline daily at 02:30 UTC against a hosted
Postgres instance, and can also be triggered manually for an arbitrary date. The
scheduler decides which date to process and passes it in; no pipeline function
ever calls `date.today()`, which keeps backfills and a future orchestrator
migration straightforward.

A non-zero exit marks the workflow run as failed and triggers GitHub's failure
notification.

## Design constraints

- All database access goes through `db.py`; nothing else imports psycopg
- Extract, transform, validate and load are separate modules, each callable alone
- Cities live in config, not in pipeline code
- All configuration comes from environment variables
- Every function takes an explicit `run_date`