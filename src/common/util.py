import os, re, datetime
from unidecode import unidecode
from pathlib import Path


def mkdir(path):
    os.makedirs(path, exist_ok=True)
    return path


def all_files(dir_path: str):
    return [str(f) for f in Path(dir_path).rglob('*') if f.is_file()]


def file_lines(path):
    with open(path, 'r') as file:
        return [line.strip() for line in file.readlines()]


def filename_before_timestamp(path: str):
    search = re.search(r'.*/(.*)[~-]', path)
    return search.group(1) if search else None


def timestamp():
    return datetime.datetime.now().strftime('%Y%m%dT%H%M%S')


def normalize(string: str):
    return unidecode(string).lower() if string else None
