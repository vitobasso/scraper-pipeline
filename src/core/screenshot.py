from src.core.config import config
from src.core.browser_session import browser_page

after_load_timeout = config.get('screenshot.browser.after_load_timeout')

async def screenshot(proxy: str, url: str, path: str):
    async with browser_page(proxy, url, wait_until='load') as page:
            await page.wait_for_timeout(after_load_timeout)
            await page.screenshot(path=path, full_page=True, animations='disabled')
