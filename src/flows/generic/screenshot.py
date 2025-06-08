import datetime, asyncio, sys
from src.core.proxies import random_proxy
from src.core.browser_session import browser_page, error_name
from src.core.util import mkdir

after_load_timeout = 0


def sync_screenshot(output_dir: str, ticker: str, url: str):
    asyncio.run(_screenshot(*params(output_dir, ticker, url)))


def params(screenshot_dir: str, ticker: str, url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'{ticker}-{timestamp}.png'
    screenshot_dir = mkdir(f'{screenshot_dir}/screenshots/awaiting-validation')
    output_path = f'{screenshot_dir}/{filename}'
    proxy = random_proxy()
    return proxy, url, output_path


async def _screenshot(proxy: str, url: str, path: str):
    print(f'taking screenshot, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with browser_page(proxy, url, wait_until='load') as page:
            await page.wait_for_timeout(after_load_timeout)
            await page.screenshot(path=path, full_page=True, animations='disabled')
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)
