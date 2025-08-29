import asyncio
from pathlib import Path

from src.common.date_util import timestamp
from src.scraper.core import paths
from src.scraper.core.logs import log
from src.scraper.services.browser import common_ancestor, error_name, page_goto
from src.scraper.services.proxies import random_proxy

after_load_timeout = 0


def ss_full_page(ticker: str, pipeline: str, url: str):
    path = output_path(ticker, pipeline)
    asyncio.run(_screenshot_full_page(random_proxy(pipeline), url, path, pipeline, ticker))


def ss_common_ancestor(ticker: str, pipeline: str, url: str, texts):
    path = output_path(ticker, pipeline)
    asyncio.run(_screenshot_common_ancestor(random_proxy(pipeline), url, texts, path, pipeline, ticker))


def output_path(ticker: str, pipeline: str):
    return paths.stage_dir_for(ticker, pipeline, "extraction") / f"{timestamp()}.png"


async def _screenshot_full_page(proxy: str, url: str, path: Path, pipeline: str, ticker: str):
    print(f"taking screenshot, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url, wait_until="load") as page:
            await page.wait_for_timeout(after_load_timeout)
            await page.screenshot(path=path, full_page=True, animations="disabled")
    except Exception as e:
        log(error_name(e), ticker, pipeline)


async def _screenshot_common_ancestor(proxy: str, url: str, texts: list, path: Path, pipeline: str, ticker: str):
    print(f"taking screenshot, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url, wait_until="domcontentloaded") as page:
            locator = common_ancestor(page, texts)
            await locator.screenshot(path=path)
    except Exception as e:
        log(error_name(e), ticker, pipeline)
