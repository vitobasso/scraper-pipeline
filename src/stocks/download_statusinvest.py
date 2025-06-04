from playwright.async_api import async_playwright, ProxySettings
from src.core.config import config
from src.core.browser_session import browser_page

load_timeout = config.get('screenshot.browser.load_timeout')
after_load_timeout = config.get('screenshot.browser.after_load_timeout')

async def download(proxy: str, path: str):
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
