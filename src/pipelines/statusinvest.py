import asyncio
from src.config import output_root
from src.common.util import mkdir, timestamp
from src.scheduler import Pipeline, seed_task
from src.services.proxies import random_proxy
from src.services.browser import page_goto, click, click_download

name = 'statusinvest'
output_dir = mkdir(f'{output_root}/{name}')


def pipeline() -> Pipeline:
    return {
        'name': name,
        'tasks': [
            seed_task(sync_download, output_dir),
        ]
    }

def sync_download():
    asyncio.run(download())


async def download():
    path = f'{output_dir}/{timestamp()}.csv'
    proxy = random_proxy()
    print(f'downloading csv, path: {path}, proxy: {proxy}')
    return await _download(proxy, path)


async def _download(proxy: str, path: str):
    async with page_goto(proxy, 'https://statusinvest.com.br/acoes/busca-avancada') as page:
        await click(page, 'button', 'Buscar')
        await click_download(path, page, 'a', 'DOWNLOAD')
