from datetime import date

import requests

from tollgate import config

API_URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_city_weather(city: str, run_date: date) -> list[dict]:
    coords = config.CITIES[city]
    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "start_date": run_date.isoformat(),
        "end_date": run_date.isoformat(),
        "hourly": "temperature_2m,relative_humidity_2m",
        "timezone": "UTC",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    hourly = payload["hourly"]
    readings = []
    for ts, temp_c, humidity in zip(
        hourly["time"], hourly["temperature_2m"], hourly["relative_humidity_2m"]
    ):
        readings.append(
            {"city": city, "ts": ts, "temp_c": temp_c, "humidity": humidity}
        )
    return readings


def fetch_all_cities(run_date: date) -> list[dict]:
    readings = []
    for city in config.CITIES:
        readings.extend(fetch_city_weather(city, run_date))
    return readings