from dotenv import load_dotenv

load_dotenv()
import os

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_NAME = os.environ["POSTGRES_DB"]
DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]

CITIES = {
    "Delhi":     {"latitude": 28.6139, "longitude": 77.2090},
    "Mumbai":    {"latitude": 19.0760, "longitude": 72.8777},
    "Kolkata":   {"latitude": 22.5726, "longitude": 88.3639},
    "Chennai":   {"latitude": 13.0827, "longitude": 80.2707},
    "Bengaluru": {"latitude": 12.9716, "longitude": 77.5946},
    "Hyderabad": {"latitude": 17.3850, "longitude": 78.4867},
    "Pune":      {"latitude": 18.5204, "longitude": 73.8567},
    "Ahmedabad": {"latitude": 23.0225, "longitude": 72.5714},
    "Jaipur":    {"latitude": 26.9124, "longitude": 75.7873},
    "Bhubaneswar": {"latitude": 20.2961, "longitude": 85.8245},
}