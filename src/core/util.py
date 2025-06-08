import os, re, glob
from pathlib import Path


def mkdir(path):
    os.makedirs(path, exist_ok=True)
    return path


def all_files(dir_path: str):
    return [str(f) for f in Path(dir_path).rglob('*') if f.is_file()]


def get_ticker(path: str):
    return re.match(r'.*/(\w+)+.*', path).group(1)
