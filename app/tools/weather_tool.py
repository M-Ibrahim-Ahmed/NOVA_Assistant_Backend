import httpx


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


async def get_weather(
    latitude: float,
    longitude: float,
) -> str:

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        # Current weather
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "weather_code,"
            "wind_speed_10m"
        ),

        # Daily forecast
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "precipitation_sum"
        ),

        # Get enough forecast days for upcoming questions
        "forecast_days": 7,

        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",

        # Automatically use the location's timezone
        "timezone": "auto",
    }

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

    # =====================================================
    # CURRENT WEATHER
    # =====================================================

    current = data["current"]

    current_weather_code = current["weather_code"]

    current_description = get_weather_description(
        current_weather_code
    )

    result = (
        "CURRENT WEATHER\n"
        f"Temperature: {current['temperature_2m']}°C\n"
        f"Feels like: {current['apparent_temperature']}°C\n"
        f"Humidity: {current['relative_humidity_2m']}%\n"
        f"Wind speed: {current['wind_speed_10m']} km/h\n"
        f"Conditions: {current_description}\n\n"
    )

    # =====================================================
    # DAILY FORECAST
    # =====================================================

    daily = data["daily"]

    dates = daily["time"]
    weather_codes = daily["weather_code"]
    max_temperatures = daily["temperature_2m_max"]
    min_temperatures = daily["temperature_2m_min"]
    precipitation_probabilities = daily[
        "precipitation_probability_max"
    ]
    precipitation_amounts = daily[
        "precipitation_sum"
    ]

    result += "7-DAY FORECAST\n"

    for i in range(len(dates)):

        description = get_weather_description(
            weather_codes[i]
        )

        result += (
            f"{dates[i]}: "
            f"{description}, "
            f"High {max_temperatures[i]}°C, "
            f"Low {min_temperatures[i]}°C, "
            f"Rain probability "
            f"{precipitation_probabilities[i]}%, "
            f"Precipitation "
            f"{precipitation_amounts[i]} mm\n"
        )

    return result