import re
from datetime import datetime
from pathlib import Path

from src.config import timestamp_format


def mkdir(path: Path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def all_files(dir_path: Path):
    return [f for f in dir_path.rglob('*') if f.is_file()]


def last_file(dir_path: Path) -> Path | None:
    if not dir_path.exists():
        return None
    files = list(dir_path.glob("*"))
    return max(files) if files else None


def file_lines(path: Path):
    with open(path, 'r') as file:
        return [line.strip() for line in file.readlines()]


def filename_before_timestamp(file: Path):
    search = re.search(r'.*/(.*)[~-]', str(file))
    return search.group(1) if search else None


def datetime_from_filename(file: Path) -> datetime:
    return to_datetime(file.stem)


def to_datetime(timestamp_str: str):
    return datetime.strptime(timestamp_str, timestamp_format)


def timestamp() -> str:
    return datetime.now().strftime(timestamp_format)
