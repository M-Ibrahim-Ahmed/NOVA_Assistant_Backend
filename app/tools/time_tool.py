
from contextvars import ContextVar

from app.services.time_service import (
    get_datetime_context,
    get_datetime_data,
)


_current_time_card: ContextVar[dict | None] = ContextVar(
    "nova_time_card",
    default=None,
)


def clear_time_result() -> None:
    _current_time_card.set(None)


def get_last_time_result() -> dict | None:
    return _current_time_card.get()


def get_current_time() -> str:
    # Capture time-card data when NOVA invokes
    # the existing time tool.
    _current_time_card.set(
        get_datetime_data()
    )

    # Preserve the existing spoken-response format.
    return get_datetime_context()
