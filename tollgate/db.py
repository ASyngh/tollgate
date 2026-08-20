from contextlib import contextmanager

import psycopg

from tollgate import config


def connection_string() -> str:
    if config.DATABASE_URL:
        return config.DATABASE_URL
    return (
        f"host={config.DB_HOST} "
        f"port={config.DB_PORT} "
        f"dbname={config.DB_NAME} "
        f"user={config.DB_USER} "
        f"password={config.DB_PASSWORD}"
    )


@contextmanager
def get_connection():
    conn = psycopg.connect(connection_string())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()