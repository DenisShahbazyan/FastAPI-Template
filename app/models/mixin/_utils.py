from datetime import datetime, timezone


def get_current_dt_utc() -> datetime:
    """Возвращает текущее время в UTC.

    Returns:
        datetime: Текущее время в UTC
    """
    dt = datetime.now(tz=timezone.utc)
    return dt.replace(tzinfo=None)
