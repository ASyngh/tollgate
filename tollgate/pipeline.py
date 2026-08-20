import sys
from datetime import date, datetime, timezone

from tollgate.checks import QualityCheckFailed, run_checks
from tollgate.db import get_connection
from tollgate.extract import fetch_all_cities
from tollgate.load import load_daily_aggregates, load_raw_weather
from tollgate.transform import build_daily_aggregates

START_RUN_SQL = """
INSERT INTO run_log (run_date, started_at, status)
VALUES (%(run_date)s, %(started_at)s, 'running')
RETURNING run_id
"""

FINISH_RUN_SQL = """
UPDATE run_log
SET finished_at    = %(finished_at)s,
    status         = %(status)s,
    rows_extracted = %(rows_extracted)s,
    rows_loaded    = %(rows_loaded)s,
    failure_reason = %(failure_reason)s
WHERE run_id = %(run_id)s
"""


def start_run(run_date: date) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                START_RUN_SQL,
                {"run_date": run_date, "started_at": datetime.now(timezone.utc)},
            )
            return cur.fetchone()[0]


def finish_run(
    run_id: int,
    status: str,
    rows_extracted: int,
    rows_loaded: int,
    failure_reason: str | None,
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                FINISH_RUN_SQL,
                {
                    "run_id": run_id,
                    "finished_at": datetime.now(timezone.utc),
                    "status": status,
                    "rows_extracted": rows_extracted,
                    "rows_loaded": rows_loaded,
                    "failure_reason": failure_reason,
                },
            )


def run(run_date: date) -> int:
    run_id = start_run(run_date)
    rows_extracted = 0
    rows_loaded = 0

    try:
        readings = fetch_all_cities(run_date)
        rows_extracted = len(readings)
        load_raw_weather(readings)
        print(f"extracted and landed {rows_extracted} readings")

        aggregates = build_daily_aggregates(run_date)
        print(f"built {len(aggregates)} daily aggregates")

        run_checks(aggregates)
        print("quality checks passed")

        rows_loaded = load_daily_aggregates(aggregates)
        print(f"loaded {rows_loaded} rows into daily_city_weather")

    except QualityCheckFailed as exc:
        finish_run(run_id, "failed", rows_extracted, 0, f"quality check failed: {exc}")
        print(f"QUALITY CHECK FAILED: {exc}", file=sys.stderr)
        return 1

    except Exception as exc:
        finish_run(run_id, "failed", rows_extracted, 0, f"{type(exc).__name__}: {exc}")
        print(f"PIPELINE ERROR: {exc}", file=sys.stderr)
        return 1

    finish_run(run_id, "success", rows_extracted, rows_loaded, None)
    print(f"run {run_id} succeeded")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python -m tollgate.pipeline YYYY-MM-DD", file=sys.stderr)
        sys.exit(2)
    sys.exit(run(date.fromisoformat(sys.argv[1])))