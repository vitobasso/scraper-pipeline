import os, sys, time, datetime, random, re, urllib.request
from pathlib import Path

from src import config
from src.core import util
from src.core.util import mkdir

list_dir = mkdir(Path(config.output_root) / '_proxy-list')
refresh_seconds = 2 * 60 * 60

_proxies = None


def random_proxy():
    return random.choice(_init()) if config.use_proxies else None


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
    timestamp = datetime.datetime.now().strftime(config.timestamp_format)
    download_url = config.proxies_url
    name = _extract_name(download_url)
    path = list_dir / f'proxify-{name}-{timestamp}.txt'
    print(f'downloading proxy list, url: {download_url}, path: {path}')
    urllib.request.urlretrieve(download_url, path)


def _extract_name(path):
    return re.search('/(\\w+)/data.txt', path).group(1)
