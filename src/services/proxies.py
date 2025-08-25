import os, sys, time, datetime, random, re, urllib.request
from pathlib import Path

from src import config
from src.core import util
from src.core.util import mkdir

list_dir = mkdir(Path(config.output_root) / '_proxy-list')
refresh_seconds = 2 * 60 * 60

_proxies = None


def random_proxy(pipeline):
    return random.choice(_init()) if _is_enabled_for(pipeline) else None


def _is_enabled_for(pipeline):
    return config.use_proxies_for_pipeline.get(pipeline, config.use_proxies)


def _init():
    global _proxies
    if not _proxies:
        _proxies = _refresh()
    return _proxies


def _refresh():
    if not _validate_latest_file():
        _download_list()
    if not _validate_latest_file():
        print('failed to download proxy lists', file=sys.stderr)
        sys.exit(1)
    file = util.last_file(list_dir)
    return _load_list(file)


def _validate_latest_file():
    file = util.last_file(list_dir)
    return file and _validate_file(file)


def _validate_file(path: Path):
    file_time = os.path.getctime(path)
    file_age = time.time() - file_time
    return file_age < refresh_seconds


def _load_list(path: Path):
    with open(path) as f:
        return f.read().splitlines()


def _download_list():
    for url in config.proxy_urls:
        path = _file_path(url)
        print(f'downloading proxy list, url: {url}, path: {path}')
        if data := _download_url(url):
            path.write_bytes(data)
            break


def _download_url(url: str):
    with urllib.request.urlopen(url) as r:
        return r.read()


def _file_path(url: str) -> Path:
    timestamp = datetime.datetime.now().strftime(config.timestamp_format)
    name = _name_from_url(url)
    return list_dir / f'proxify-{name}-{timestamp}.txt'


def _name_from_url(path):
    return re.search('/(\\w+)/data.txt', path).group(1)
