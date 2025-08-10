import asyncio

from src.common.logs import log
from src.common.util import mkdir, timestamp
from src.common.validate_data import valid_data_dir
from src.config import output_root
from src.scheduler import Pipeline, seed_task, seed_progress
from src.services.browser import page_goto, click, click_download, error_name
from src.services.proxies import random_proxy

name = 'statusinvest'
output_dir = mkdir(f'{output_root}/{name}')
completed_dir = valid_data_dir(output_dir)


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            seed_task(sync_download, completed_dir),
        ],
        progress=seed_progress(output_dir)
    )


def sync_download():
    asyncio.run(download())


async def download():
    path = f'{completed_dir}/{timestamp()}.csv'
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
