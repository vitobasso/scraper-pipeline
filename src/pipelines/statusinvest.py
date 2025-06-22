import asyncio, csv, re, sys
from src.config import output_root
from src.common.util import mkdir, timestamp, all_files
from src.scheduler import Pipeline, seed_task, seed_progress
from src.services.proxies import random_proxy
from src.services.browser import page_goto, click, click_download, error_name

name = 'statusinvest'
output_dir = mkdir(f'{output_root}/{name}')


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            seed_task(sync_download, output_dir),
        ],
        progress=seed_progress(output_dir)
    )


def sync_download():
    asyncio.run(download())


async def download():
    path = f'{output_dir}/{timestamp()}.csv'
    proxy = random_proxy()
    return await _download(proxy, path)


async def _download(proxy: str, path: str):
    print(f'downloading csv, path: {path}, proxy: {proxy}')
    try:
        async with page_goto(proxy, 'https://statusinvest.com.br/acoes/busca-avancada') as page:
            await click(page, 'button', 'Buscar')
            await click_download(path, page, 'a', 'DOWNLOAD')
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)


def to_spreadsheet():
    files = all_files(output_dir)
    if files:
        with open(files[0]) as file:
            rows = [row for row in csv.reader(file, delimiter=';')]
            return _clean_data(rows)
    else:
        return []


def _clean_data(data):
    return [[_clean_numbers(value) for value in row]
            for row in data]


def _clean_numbers(value):
    replaced = str(value).replace(".", "").replace(",", ".")
    return _convert_if_number(replaced)


def _convert_if_number(value):
    if isinstance(value, str) and re.fullmatch(r'^-?\d+\.?\d*$', value):
        return float(value)
    return value
