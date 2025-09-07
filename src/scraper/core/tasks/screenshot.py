import asyncio
from collections.abc import Callable

from src.scraper.core import paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline, TaskFactory
from src.scraper.core.tasks.base import source_task
from src.scraper.services.browser import common_ancestor, error_name, page_goto
from src.scraper.services.proxies import random_proxy

after_load_timeout = 0


def screenshot(get_url: Callable[[str], str], scope_selectors: list[str] | None = None) -> TaskFactory:
    """
    get_url: takes a ticker and returns a url.
    scope_selectors: list of strings present in the target region of the page.
                     their common ancestor will be used to limit the screenshot.
    """
    if scope_selectors:
        execute = lambda pipe, ticker: _sync_common_ancestor(ticker, pipe, get_url(ticker), scope_selectors)
    else:
        execute = lambda pipe, ticker: _sync_full_page(ticker, pipe, get_url(ticker))
    return source_task(execute)


def _sync_full_page(ticker: str, pipe: Pipeline, url: str):
    asyncio.run(_full_page(url, pipe, ticker))


def _sync_common_ancestor(ticker: str, pipe: Pipeline, url: str, texts: list[str]):
    asyncio.run(_common_ancestor(url, texts, pipe, ticker))


async def _full_page(url: str, pipe: Pipeline, ticker: str):
    path = _output_path(pipe, ticker)
    proxy = random_proxy(pipe)
    print(f"taking screenshot, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url, wait_until="load") as page:
            await page.wait_for_timeout(after_load_timeout)
            await page.screenshot(path=path, full_page=True, animations="disabled")
    except Exception as e:
        log(error_name(e), ticker, pipe)


async def _common_ancestor(url: str, scope_selectors: list[str], pipe: Pipeline, ticker: str):
    path = _output_path(pipe, ticker)
    proxy = random_proxy(pipe)
    print(f"taking screenshot, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url, wait_until="domcontentloaded") as page:
            locator = common_ancestor(page, scope_selectors)
            await locator.screenshot(path=path)
    except Exception as e:
        log(error_name(e), ticker, pipe)


def _output_path(pipe: Pipeline, ticker: str):
    return paths.for_pipe(pipe, ticker).output_file("extraction", "png")
