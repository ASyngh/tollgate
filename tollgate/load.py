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