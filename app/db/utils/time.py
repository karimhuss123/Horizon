from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo("America/New_York")

def current_datetime_et() -> datetime:
    return datetime.now(EASTERN)

def time_diff(start: datetime, end: datetime) -> dict:
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("Both datetime objects must be timezone-aware")
    return end - start 

def is_before(t1: datetime, t2: datetime) -> bool:
    if t1.tzinfo is None or t2.tzinfo is None:
        raise ValueError("Both datetime objects must be timezone-aware")
    return t1 < t2

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

def get_today_date() -> date:
    return datetime.now(EASTERN).date()

def start_of_day(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    return datetime(dt.year, dt.month, dt.day, tzinfo=EASTERN)

def end_of_day(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    return add_to_datetime(datetime(dt.year, dt.month, dt.day, tzinfo=EASTERN), days=1)

def day_bounds_from_date(d: date) -> tuple[datetime, datetime]:
    day_start = datetime(d.year, d.month, d.day, tzinfo=EASTERN)
    day_end = add_to_datetime(day_start, days=1)
    return day_start, day_end
