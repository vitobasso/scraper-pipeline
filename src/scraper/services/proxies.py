import datetime
import os
import random
import sys
import time
import urllib.request
from pathlib import Path

from src.common import config
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.util import files

list_dir = files.mkdir(Path(config.data_root) / "_proxy-list")

_proxies = None


def random_proxy(pipe: Pipeline):
    return random.choice(_init()) if _is_enabled_for(pipe) else None


def _is_enabled_for(pipe: Pipeline):
    return config.use_proxies_for_pipeline.get(pipe.name, config.use_proxies)


def _init():
    global _proxies
    if not _proxies:
        _proxies = _refresh()
    return _proxies


def _refresh() -> list[str]:
    if not _validate_latest_file():
        _download_list()
    if not _validate_latest_file():
        print("failed to download proxy lists", file=sys.stderr)
        sys.exit(1)
    file = files.last_file(list_dir)
    return _load_list(file)


def _validate_latest_file():
    file = files.last_file(list_dir)
    return file and _validate_file(file)


def _validate_file(path: Path):
    file_time = os.path.getctime(path)
    file_age = time.time() - file_time
    return file_age < config.proxy_refresh_seconds


def _load_list(path: Path) -> list[str]:
    with open(path) as f:
        return f.read().splitlines()


def _download_list():
    for url in config.proxy_urls:
        path = _file_path()
        print(f"downloading proxy list, url: {url}, path: {path}")
        if data := _download_url(url):
            path.write_bytes(data)
            break


def _download_url(url: str):
    with urllib.request.urlopen(url) as r:
        return r.read()


def _file_path() -> Path:
    timestamp = datetime.datetime.now().strftime(config.timestamp_format)
    return list_dir / f"{timestamp}.txt"
