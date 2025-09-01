import asyncio

from src.common.util.date_util import timestamp
from src.scraper.core import paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.services.browser import common_ancestor, error_name, page_goto
from src.scraper.services.proxies import random_proxy

after_load_timeout = 0


def ss_full_page(ticker: str, pipe: Pipeline, url: str):
    asyncio.run(_screenshot_full_page(url, pipe, ticker))


def ss_common_ancestor(ticker: str, pipe: Pipeline, url: str, texts):
    asyncio.run(_screenshot_common_ancestor(url, texts, pipe, ticker))


def output_path(ticker: str, pipe: Pipeline):
    return paths.for_pipe(pipe, ticker).stage_dir("extraction") / f"{timestamp()}.png"


async def _screenshot_full_page(url: str, pipe: Pipeline, ticker: str):
    path = output_path(ticker, pipe)
    proxy = random_proxy(pipe)
    print(f"taking screenshot, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url, wait_until="load") as page:
            await page.wait_for_timeout(after_load_timeout)
            await page.screenshot(path=path, full_page=True, animations="disabled")
    except Exception as e:
        log(error_name(e), ticker, pipe)


async def _screenshot_common_ancestor(url: str, texts: list, pipe: Pipeline, ticker: str):
    path = output_path(ticker, pipe)
    proxy = random_proxy(pipe)
    print(f"taking screenshot, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url, wait_until="domcontentloaded") as page:
            locator = common_ancestor(page, texts)
            await locator.screenshot(path=path)
    except Exception as e:
        log(error_name(e), ticker, pipe)
