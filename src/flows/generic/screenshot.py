import datetime, asyncio, sys
from src.config import output_dir
from src.core.proxies import random_proxy
from src.core.browser_session import browser_page, error_name

after_load_timeout = 0


def sync_screenshot(key: str, url: str):
    asyncio.run(_screenshot(*params(key, url)))


def params(key: str, url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'{key}-{timestamp}.png'
    output_path = f'{output_dir}/screenshots/awaiting-validation/{filename}'
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
