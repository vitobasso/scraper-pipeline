import os, glob, sys, time, datetime, random, re, urllib.request
from pathlib import Path
from src.config import output_root, proxies_url as download_url

list_dir = f'{output_root}/proxy-list'
timestamp_format = '%Y%m%dT%H%M%S'
refresh_seconds = 2 * 60 * 60

_proxies = None


def random_proxy():
    return random.choice(_get_proxies())


def _get_proxies():
    global _proxies
    if not _proxies:
        _proxies = _init()
    return _proxies


def _init():
    if not _validate_latest_file():
        _download_list()
    if not _validate_latest_file():
        print('failed to download proxy lists', file=sys.stderr)
        sys.exit(1)
    file = _latest_file()
    return _load_list(file)


def _validate_latest_file():
    file = _latest_file()
    return file and _validate_file(file)


def _validate_file(path: str):
    file_time = os.path.getctime(path)
    file_age = time.time() - file_time
    return file_age < refresh_seconds


def _latest_file():
    files = glob.glob(f'{list_dir}/*')
    return max(files) if files else None


def _load_list(path: str):
    with open(path) as f:
        return f.read().splitlines()


def _download_list():
    timestamp = datetime.datetime.now().strftime(timestamp_format)
    name = _extract_name(download_url)
    path = f'{list_dir}/proxify-{name}-{timestamp}.txt'
    Path(list_dir).mkdir(parents=True, exist_ok=True)
    print(f'downloading proxy list, url: {download_url}, path: {path}')
    urllib.request.urlretrieve(download_url, path)


def _extract_name(path):
    return re.search('/(\\w+)/data.txt', path).group(1)
