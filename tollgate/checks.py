MIN_TEMP_C = -50
MAX_TEMP_C = 60
EXPECTED_READINGS_PER_DAY = 24


class QualityCheckFailed(Exception):
    """Raised when one or more quality checks fail."""


def check_reading_count(rows: list[dict]) -> list[str]:
    problems = []
    for row in rows:
        if row["reading_count"] != EXPECTED_READINGS_PER_DAY:
            problems.append(
                f"{row['city']}: expected {EXPECTED_READINGS_PER_DAY} readings, "
                f"got {row['reading_count']}"
            )
    return problems


def check_no_null_keys(rows: list[dict]) -> list[str]:
    problems = []
    for row in rows:
        if row["city"] is None or row["day"] is None:
            problems.append(f"null key found in row: {row}")
    return problems


def check_temperature_range(rows: list[dict]) -> list[str]:
    problems = []
    for row in rows:
        for field in ("min_temp_c", "max_temp_c", "avg_temp_c"):
            value = row[field]
            if value is None:
                problems.append(f"{row['city']}: {field} is null")
            elif not (MIN_TEMP_C <= value <= MAX_TEMP_C):
                problems.append(
                    f"{row['city']}: {field}={value} outside "
                    f"[{MIN_TEMP_C}, {MAX_TEMP_C}]"
                )
    return problems


def check_no_duplicate_city_day(rows: list[dict]) -> list[str]:
    seen = set()
    problems = []
    for row in rows:
        key = (row["city"], row["day"])
        if key in seen:
            problems.append(f"duplicate row for {key}")
        seen.add(key)
    return problems


CHECKS = [
    check_reading_count,
    check_no_null_keys,
    check_temperature_range,
    check_no_duplicate_city_day,
]


def run_checks(rows: list[dict]) -> None:
    problems = []
    for check in CHECKS:
        problems.extend(check(rows))
    if problems:
        raise QualityCheckFailed("; ".join(problems))