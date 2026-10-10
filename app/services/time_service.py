
from datetime import datetime
from zoneinfo import ZoneInfo

PAKISTAN_TIMEZONE = ZoneInfo("Asia/Karachi")


def get_current_datetime() -> datetime:
    return datetime.now(PAKISTAN_TIMEZONE)


def get_current_date() -> str:
    return get_current_datetime().strftime("%A, %B %d, %Y")


def get_current_time() -> str:
    return get_current_datetime().strftime("%I:%M %p")


def get_datetime_data() -> dict:
    """Structured data for the native Android time card."""
    now = get_current_datetime()

    return {
        "time": now.strftime("%I:%M %p"),
        "date": now.strftime("%A, %B %d, %Y"),
        "day": now.strftime("%A"),
        "timezone": "Asia/Karachi",
        "timezone_label": "Pakistan Standard Time",
        "utc_offset": "UTC+05:00",
        "iso": now.isoformat(),
    }


def get_datetime_context() -> str:
    now = get_current_datetime()

    return (
        f"Current date: {now.strftime('%A, %B %d, %Y')}\n"
        f"Current time: {now.strftime('%I:%M %p')}\n"
        "Timezone: Asia/Karachi (UTC+05:00)"
    )
