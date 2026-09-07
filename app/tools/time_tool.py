from app.services.time_service import get_datetime_context


def get_current_time():
    return get_datetime_context()