import datetime, asyncio, sys
from src.core.proxies import random_proxy
from src.core.browser_session import page_goto, common_ancestor, error_name
from src.core.util import mkdir

after_load_timeout = 0


def ss_full_page(output_dir: str, ticker: str, url: str):
    asyncio.run(_screenshot_full_page(*params(output_dir, ticker, url)))


def ss_common_ancestor(output_dir: str, ticker: str, texts, url: str):
    proxy, url, path = params(output_dir, ticker, url)
    asyncio.run(_screenshot_common_ancestor(proxy, url, texts, path))


def params(screenshot_dir: str, ticker: str, url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'{ticker}-{timestamp}.png'
    screenshot_dir = mkdir(f'{screenshot_dir}/screenshots/awaiting-validation')
    output_path = f'{screenshot_dir}/{filename}'
    proxy = random_proxy()
    return proxy, url, output_path


async def _screenshot_full_page(proxy: str, url: str, path: str):
    print(f'taking screenshot, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with page_goto(proxy, url, wait_until='load') as page:
            await page.wait_for_timeout(after_load_timeout)
            await page.screenshot(path=path, full_page=True, animations='disabled')
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)


async def _screenshot_common_ancestor(proxy: str, url: str, texts: list, path: str):
    print(f'taking screenshot, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with page_goto(proxy, url, wait_until='domcontentloaded') as page:
            locator = common_ancestor(page, texts)
            await locator.screenshot(path=path)
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)
