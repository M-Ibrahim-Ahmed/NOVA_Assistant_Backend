from datetime import datetime
from zoneinfo import ZoneInfo


PAKISTAN_TIMEZONE = ZoneInfo("Asia/Karachi")


def get_current_datetime() -> datetime:
    return datetime.now(PAKISTAN_TIMEZONE)


def get_current_date() -> str:
    now = get_current_datetime()

    return now.strftime("%A, %B %d, %Y")


def get_current_time() -> str:
    now = get_current_datetime()

    return now.strftime("%I:%M %p")


def get_datetime_context() -> str:
    now = get_current_datetime()

    return (
        f"Current date: {now.strftime('%A, %B %d, %Y')}\n"
        f"Current time: {now.strftime('%I:%M %p')}\n"
        f"Timezone: Asia/Karachi (UTC+05:00)"
    )