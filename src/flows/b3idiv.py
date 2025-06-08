import datetime, asyncio
from src.config import output_root
from src.core.proxies import random_proxy
from src.core.browser_session import page_goto, click_download

name = 'b3idiv'
output_dir = f'{output_root}/{name}'


def sync_download():
    asyncio.run(download())


async def download():
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    path = f'{output_dir}/downloads/b3idiv-{timestamp}.csv'
    proxy = random_proxy()
    print(f'downloading csv, path: {path}, proxy: {proxy}')
    return await _download(proxy, path)


async def _download(proxy: str, path: str):
    async with page_goto(proxy, 'https://sistemaswebb3-listados.b3.com.br/indexPage/day/IDIV') as page:
        await click_download(path, page, 'a', 'Download')
