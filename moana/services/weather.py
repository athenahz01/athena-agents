"""
Weather service — Ithaca weather with outfit suggestions.
"""

import logging
import requests
from moana import config

log = logging.getLogger(__name__)


def get_weather() -> dict:
    """Fetch current weather for Ithaca, NY."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": config.WEATHER_CITY,
        "units": config.WEATHER_UNITS,
        "appid": config.OPENWEATHER_API_KEY,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    temp = round(data["main"]["temp"])
    description = data["weather"][0]["description"].title()

    return {
        "temp": temp,
        "feels_like": round(data["main"]["feels_like"]),
        "high": round(data["main"]["temp_max"]),
        "low": round(data["main"]["temp_min"]),
        "humidity": data["main"]["humidity"],
        "wind_speed": round(data["wind"]["speed"]),
        "description": description,
        "outfit_tip": _get_outfit_tip(temp, description),
    }


def _get_outfit_tip(temp: int, description: str) -> str:
    """Outfit suggestion based on weather."""
    desc = description.lower()
    rain = any(w in desc for w in ["rain", "drizzle", "shower", "thunder"])
    snow = any(w in desc for w in ["snow", "sleet", "blizzard"])

    if temp >= 80:
        base = "Sundress or linen set day ☀️"
    elif temp >= 70:
        base = "Light layers — cute top + light jacket for evening"
    elif temp >= 55:
        base = "Sweater weather! Layer up, maybe a cardigan"
    elif temp >= 40:
        base = "Coat + boots situation. Scarf would be cute"
    elif temp >= 25:
        base = "Bundle up! Heavy coat, gloves, the whole thing 🧤"
    else:
        base = "STAY WARM. Puffer coat, layers, everything 🥶"

    if rain:
        base += " + umbrella! ☂️"
    elif snow:
        base += " + waterproof boots, watch for ice 🌨️"

    return base
