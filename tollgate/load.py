from tollgate.db import get_connection

INSERT_SQL = """
INSERT INTO raw_weather (city, ts, temp_c, humidity)
VALUES (%(city)s, %(ts)s, %(temp_c)s, %(humidity)s)
ON CONFLICT (city, ts) DO NOTHING
"""


def load_raw_weather(readings: list[dict]) -> int:
    if not readings:
        return 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, readings)
    return len(readings)

UPSERT_DAILY_SQL = """
INSERT INTO daily_city_weather
    (city, day, min_temp_c, max_temp_c, avg_temp_c, reading_count, built_at)
VALUES
    (%(city)s, %(day)s, %(min_temp_c)s, %(max_temp_c)s, %(avg_temp_c)s,
     %(reading_count)s, now())
ON CONFLICT (city, day) DO UPDATE SET
    min_temp_c    = EXCLUDED.min_temp_c,
    max_temp_c    = EXCLUDED.max_temp_c,
    avg_temp_c    = EXCLUDED.avg_temp_c,
    reading_count = EXCLUDED.reading_count,
    built_at      = now()
"""


def load_daily_aggregates(rows: list[dict]) -> int:
    if not rows:
        return 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(UPSERT_DAILY_SQL, rows)
    return len(rows)