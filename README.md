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

The gate sits between the