import asyncio
from pathlib import Path

from src.core import paths
from src.core.util import timestamp
from src.services.browser import page_goto, click_download
from src.services.proxies import random_proxy

name = 'b3idiv'


def sync_download():
    asyncio.run(download())


async def download():
    path = paths.stage_dir_for("_global", name, "normalization") / f'{timestamp()}.csv'
    proxy = random_proxy(name)
    print(f'downloading csv, path: {path}, proxy: {proxy}')
    return await _download(proxy, path)


async def _download(proxy: str, path: Path):
    async with page_goto(proxy, 'https://sistemaswebb3-listados.b3.com.br/indexPage/day/IDIV') as page:
        await click_download(path, page, 'a', 'Download')
