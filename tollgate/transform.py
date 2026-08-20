from datetime import date

from tollgate.db import get_connection

AGGREGATE_SQL = """
SELECT
    city,
    %(run_date)s::date AS day,
    min(temp_c)   AS min_temp_c,
    max(temp_c)   AS max_temp_c,
    avg(temp_c)   AS avg_temp_c,
    count(*)      AS reading_count
FROM raw_weather
WHERE ts >= %(run_date)s::timestamptz
  AND ts <  (%(run_date)s::date + 1)::timestamptz
GROUP BY city
ORDER BY city
"""


def build_daily_aggregates(run_date: date) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(AGGREGATE_SQL, {"run_date": run_date})
            columns = [desc.name for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]