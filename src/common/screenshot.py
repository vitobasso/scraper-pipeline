import asyncio, sys
from src.services.proxies import random_proxy
from src.services.browser import page_goto, common_ancestor, error_name
from src.common.util import mkdir, timestamp

after_load_timeout = 0


def ss_full_page(ticker: str, url: str, output_dir: str):
    path = output_path(output_dir, ticker)
    asyncio.run(_screenshot_full_page(random_proxy(), url, path))


def ss_common_ancestor(ticker: str, url: str, texts, output_dir: str):
    path = output_path(output_dir, ticker)
    asyncio.run(_screenshot_common_ancestor(random_proxy(), url, texts, path))


def output_path(screenshot_dir: str, ticker: str):
    filename = f'{ticker}-{timestamp()}.png'
    screenshot_dir = mkdir(f'{screenshot_dir}/screenshots/awaiting-validation')
    return f'{screenshot_dir}/{filename}'


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
