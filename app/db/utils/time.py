from datetime import datetime, timezone

def current_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)

def time_diff(start: datetime, end: datetime) -> dict:
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("Both datetime objects must be timezone-aware")
    return end - start 

def is_before(t1: datetime, t2: datetime) -> bool:
    if t1.tzinfo is None or t2.tzinfo is None:
        raise ValueError("Both datetime objects must be timezone-aware")
    return t1 < t2

from datetime import datetime, timedelta

def add_to_datetime(dt: datetime, seconds: float = 0, minutes: float = 0, hours: float = 0, days: float = 0) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    offset = timedelta(
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        days=days,
    )
    return dt + offset
