CREATE TABLE IF NOT EXISTS raw_weather (
    city        text        NOT NULL,
    ts          timestamptz NOT NULL,
    temp_c      numeric,
    humidity    numeric,
    ingested_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (city, ts)
);

CREATE TABLE IF NOT EXISTS daily_city_weather (
    city          text        NOT NULL,
    day           date        NOT NULL,
    min_temp_c    numeric,
    max_temp_c    numeric,
    avg_temp_c    numeric,
    reading_count int,
    built_at      timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (city, day)
);

CREATE TABLE IF NOT EXISTS run_log (
    run_id         serial PRIMARY KEY,
    run_date       date NOT NULL,
    started_at     timestamptz NOT NULL,
    finished_at    timestamptz,
    status         text NOT NULL,
    rows_extracted int,
    rows_loaded    int,
    failure_reason text
);