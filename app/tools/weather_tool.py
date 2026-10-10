
import httpx

from contextvars import ContextVar
from typing import Any


# Weather data is isolated to the current async request.
# It is not saved globally or in conversation memory.

_weather_result: ContextVar[dict[str, Any] | None] = ContextVar(
    "nova_weather_result",
    default=None,
)


def clear_weather_result() -> None:
    _weather_result.set(None)


def get_last_weather_result() -> dict[str, Any] | None:
    return _weather_result.get()


# =========================================================
# WEATHER DESCRIPTION
# =========================================================

def get_weather_description(weather_code: int) -> str:
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    return weather_codes.get(
        weather_code,
        "Unknown conditions",
    )


# =========================================================
# WEATHER ICON
# =========================================================

def get_weather_icon(weather_code: int) -> str:
    if weather_code == 0:
        return "sun"

    if weather_code in (1, 2):
        return "partly_cloudy"

    if weather_code == 3:
        return "cloud"

    if weather_code in (45, 48):
        return "fog"

    if weather_code in (51, 53, 55, 56, 57):
        return "drizzle"

    if weather_code in (
        61, 63, 65, 66, 67,
        80, 81, 82,
    ):
        return "rain"

    if weather_code in (
        71, 73, 75, 77, 85, 86,
    ):
        return "snow"

    if weather_code in (95, 96, 99):
        return "thunderstorm"

    return "unknown"


# =========================================================
# STRUCTURED WEATHER DATA
# =========================================================

async def get_weather_data(
    latitude: float,
    longitude: float,
) -> dict[str, Any]:

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "precipitation_sum"
        ),
        "forecast_days": 7,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params=params,
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

    current = data["current"]

    weather_code = int(current["weather_code"])

    current_weather = {
        "temperature": current["temperature_2m"],
        "feels_like": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "weather_code": weather_code,
        "description": get_weather_description(
            weather_code
        ),
        "icon": get_weather_icon(weather_code),
        "time": current.get("time"),
    }

    daily = data["daily"]
    forecast = []

    for index, date in enumerate(daily["time"]):
        daily_code = int(
            daily["weather_code"][index]
        )

        forecast.append({
            "date": date,
            "max_temperature":
                daily["temperature_2m_max"][index],
            "min_temperature":
                daily["temperature_2m_min"][index],
            "rain_probability":
                daily["precipitation_probability_max"][index],
            "precipitation":
                daily["precipitation_sum"][index],
            "weather_code": daily_code,
            "description":
                get_weather_description(daily_code),
            "icon": get_weather_icon(daily_code),
        })

    result = {
        "success": True,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": data.get("timezone"),
        "current": current_weather,
        "forecast": forecast,
        "units": {
            "temperature": "°C",
            "wind_speed": "km/h",
            "precipitation": "mm",
        },
    }

    # Save for the current request's API response.
    _weather_result.set(result)

    return result


# =========================================================
# EXISTING AI WEATHER FUNCTION
# =========================================================

async def get_weather(
    latitude: float,
    longitude: float,
) -> str:

    weather_data = await get_weather_data(
        latitude=latitude,
        longitude=longitude,
    )

    current = weather_data["current"]

    result = (
        "CURRENT WEATHER\n"
        f"Temperature: {current['temperature']}°C\n"
        f"Feels like: {current['feels_like']}°C\n"
        f"Humidity: {current['humidity']}%\n"
        f"Wind speed: {current['wind_speed']} km/h\n"
        f"Conditions: {current['description']}\n\n"
    )

    result += "7-DAY FORECAST\n"

    for day in weather_data["forecast"]:
        result += (
            f"{day['date']}: "
            f"{day['description']}, "
            f"High {day['max_temperature']}°C, "
            f"Low {day['min_temperature']}°C, "
            f"Rain probability "
            f"{day['rain_probability']}%, "
            f"Precipitation "
            f"{day['precipitation']} mm\n"
        )

    return result
