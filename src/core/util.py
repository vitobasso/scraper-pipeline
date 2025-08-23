from datetime import datetime, date
from pathlib import Path

from src.config import timestamp_format


def mkdir(path: Path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def last_file(dir_path: Path) -> Path | None:
    if not dir_path.exists():
        return None
    files = list(dir_path.glob("*"))
    return max(files) if files else None


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
