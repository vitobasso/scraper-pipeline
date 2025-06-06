import datetime, asyncio
from src.config import output_dir
from src.core.proxies import random_proxy
from src.core.browser_session import browser_page, click_download

def sync_download():
    asyncio.run(download())

async def download():
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    path = f'{output_dir}/downloads/b3idiv-{timestamp}.csv'
    proxy = random_proxy()
    print(f'downloading csv, path: {path}, proxy: {proxy}')
    return await _download(proxy, path)

async def _download(proxy: str, path: str):
    async with browser_page(proxy, 'https://sistemaswebb3-listados.b3.com.br/indexPage/day/IDIV') as page:
        await click_download(path, page, 'a', 'Download')

