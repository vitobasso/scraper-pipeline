import datetime, asyncio
from src.core.proxies import random_proxy
from src.core.browser_session import browser_page

def sync_download():
    asyncio.run(download())

async def download():
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    path = f'output/downloads/statusinvest-{timestamp}.csv'
    proxy = random_proxy()
    print(f'downloading csv, path: {path}, proxy: {proxy}')
    return await _download(proxy, path)

async def _download(proxy: str, path: str):
    async with browser_page(proxy, 'https://statusinvest.com.br/acoes/busca-avancada') as page:

            # 1. click "Buscar" to reveal the "Download" button
            search_button = page.locator("button", has_text="Buscar")
            await search_button.wait_for(state="visible")
            await search_button.click()

            # 2. click "Download"
            download_button = page.locator("a", has_text="DOWNLOAD")
            await download_button.wait_for(state="visible")
            async with page.expect_download() as download_info:
                await download_button.click()
            download = await download_info.value
            await download.save_as(path)
