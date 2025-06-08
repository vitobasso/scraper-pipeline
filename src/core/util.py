import os, re, datetime
from pathlib import Path


def mkdir(path):
    os.makedirs(path, exist_ok=True)
    return path


def all_files(dir_path: str):
    return [str(f) for f in Path(dir_path).rglob('*') if f.is_file()]


def filename_before_timestamp(path: str):
    search = re.search(r'.*/(.*)[~-]', path)
    return search.group(1) if search else None


def timestamp():
    return datetime.datetime.now().strftime('%Y%m%dT%H%M%S')