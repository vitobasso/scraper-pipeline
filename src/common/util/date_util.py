from datetime import date, datetime
from pathlib import Path

from src.common.config import timestamp_format


def date_from_filename(file: Path) -> date:
    return datetime_from(file.stem).date()


def datetime_from_filename(file: Path) -> datetime:
    return datetime_from(file.stem)


def date_from(timestamp_str: str) -> date:
    return datetime_from(timestamp_str).date()


def datetime_from(timestamp_str: str):
    return datetime.strptime(timestamp_str, timestamp_format)


def timestamp() -> str:
    return datetime.now().strftime(timestamp_format)
