import asyncio
import csv
import os
import re
from pathlib import Path

import unicodedata

from src.common.logs import log
from src.common.util import mkdir, timestamp
from src.common.validate_data import valid_data_dir
from src.config import output_root
from src.scheduler import Pipeline, seed_task, seed_progress, file_task
from src.services.browser import page_goto, click, click_download, error_name
from src.services.proxies import random_proxy

name = 'statusinvest'
output_dir = mkdir(f'{output_root}/{name}')
awaiting_dir = mkdir(f'{output_dir}/data/awaiting_normalization')
consumed_dir = mkdir(f'{output_dir}/data/consumed')
ready_dir = valid_data_dir(output_dir)


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            seed_task(sync_download, f'{output_dir}/data'),
            file_task(normalize_data, awaiting_dir),
        ],
        progress=seed_progress(output_dir)
    )


def sync_download():
    asyncio.run(download())


async def download():
    path = f'{awaiting_dir}/{timestamp()}.csv'
    proxy = random_proxy()
    return await _download(proxy, path)


async def _download(proxy: str, path: str):
    print(f'downloading csv, path: {path}, proxy: {proxy}')
    try:
        async with page_goto(proxy, 'https://statusinvest.com.br/acoes/busca-avancada') as page:
            await click(page, 'button', 'Buscar')
            await click_download(path, page, 'a', 'DOWNLOAD')
    except Exception as e:
        log(error_name(e), name)


def normalize_data(path: str):
    print(f'normalizing csv, path: {path}')
    try:
        input_path = Path(path)
        ready_path = Path(ready_dir, input_path.name)
        _normalize_data(input_path, ready_path)
        consumed_path = Path(consumed_dir) / input_path.name
        os.rename(str(input_path), str(consumed_path))
    except Exception as e:
        log(str(e), name)


def _normalize_data(file_path: Path, output_path: Path):
    with file_path.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        headers = next(reader)
        headers = [_normalize_header(h) for h in headers]
        rows = []
        for row in reader:
            ticker, *rest = row
            values = [_normalize_value(v) for v in rest]
            rows.append([ticker] + values)
    with output_path.open("w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out, delimiter=";")
        writer.writerow(headers)
        writer.writerows(rows)


def _normalize_header(header: str) -> str:
    header = header.lower()
    # remove accents
    header = ''.join(
        c for c in unicodedata.normalize('NFKD', header)
        if not unicodedata.combining(c)
    )
    # replace symbols with space
    header = re.sub(r'[^a-z0-9]+', ' ', header)
    # trim and replace spaces with underscores
    return "_".join(header.strip().split())


def _normalize_value(value: str):
    try:
        return float(value.replace(".", "").replace(",", "."))
    except ValueError:
        return value
