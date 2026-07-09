from datetime import datetime


def format_datetime(dt: datetime, fmt: str) -> str:
    return dt.astimezone().strftime(fmt)
