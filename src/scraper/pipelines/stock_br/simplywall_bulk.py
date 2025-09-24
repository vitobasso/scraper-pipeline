import asyncio
from collections.abc import Callable
from pathlib import Path

from playwright.async_api import Page

from src.scraper.core import paths_pipe
from src.scraper.core.logs import log
from src.scraper.core.paths import processed_path
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import normalization
from src.scraper.core.tasks.base import global_task, intermediate_task
from src.scraper.core.tasks.normalization import normalize_json_split
from src.scraper.core.tasks.validation import validate_json
from src.scraper.core.util.files import read_lines, write_json, write_lines
from src.scraper.services import browser
from src.scraper.services.proxies import random_proxy


def pipeline():
    return Pipeline.from_caller(
        tasks=[
            global_task(scrape_first),
            intermediate_task(scrape_retry, "extraction"),
            normalize_json_split(normalize, "simplywall"),
            validate_json(schema, "ready"),
        ],
    )


def scrape_first(pipe: Pipeline):
    proxy = random_proxy(pipe)
    url = "https://simplywall.st/stocks/br"
    new_path = lambda: paths_pipe.for_pipe(pipe, "_global").output_file("normalization", "json")
    asyncio.run(_scrape_first(url, new_path, proxy, pipe))


def scrape_retry(pipe: Pipeline, input_path: Path):
    proxy = random_proxy(pipe)
    new_path = lambda: paths_pipe.for_pipe(pipe, "_global").output_file("normalization", "json")
    asyncio.run(_scrape_retry(input_path, new_path, proxy, pipe))


async def _scrape_first(url: str, new_path: Callable[[], Path], proxy: str, pipe: Pipeline):
    pending_urls = set()
    try:
        async with browser.new_page(proxy) as page:
            await _intercept_backend_call(page, url, new_path(), proxy)
            pending_urls = {x async for x in _extract_urls_per_industry(page)}
            for industry_url in pending_urls.copy():
                if await _intercept_backend_call(page, industry_url, new_path(), proxy):
                    pending_urls.remove(industry_url)
    except Exception as e:
        log(browser.error_name(e), "_global", pipe)
    if pending_urls:
        pending_path = paths_pipe.for_pipe(pipe, "_global").output_file("extraction", "txt")
        write_lines(list(pending_urls), pending_path)


async def _scrape_retry(input_path: Path, new_path: Callable[[], Path], proxy: str, pipe: Pipeline):
    pending_urls = set(read_lines(input_path))
    try:
        print(f"retrying urls, path: {input_path}, proxy: {proxy}")
        async with browser.new_page(proxy) as page:
            for industry_url in pending_urls.copy():
                if await _intercept_backend_call(page, industry_url, new_path(), proxy):
                    pending_urls.remove(industry_url)
    except Exception as e:
        log(browser.error_name(e), "_global", pipe)
    input_path.rename(processed_path(input_path))
    if pending_urls:
        write_lines(list(pending_urls), input_path)


async def _extract_urls_per_industry(page: Page):
    ul = page.locator('div[data-cy-id="dropdown-basic-filter-industry"] ul[data-cy-id="dropdown-list"]').first
    links = ul.locator("li a")
    hrefs = [await a.get_attribute("href") for a in await links.all()]
    for href in hrefs[1:]:
        yield f"https://simplywall.st{href}"


async def _intercept_backend_call(page: Page, url: str, path: Path, proxy: str):
    print(f"scraping json, url: {url}, path: {path}, proxy: {proxy}")
    match_watchlist = lambda r: "/graphql" in r.url and "getWatchlist" in (r.request.post_data or "")
    match_request = lambda r: "/filter" in r.url or match_watchlist(r)
    data = await browser.expect_either(
        page, lambda page: browser.expect_json_response(page, url, match_request), lambda page: _wait_for_idle(page)
    )
    if data:
        write_json(data, path)
    return data


async def _wait_for_idle(page: Page):
    await asyncio.sleep(5)
    await browser.wait_idle(page)


def normalize(raw: dict) -> list[tuple[str, dict]]:
    data = raw.get("data", None)
    if isinstance(data, list):
        return normalize_filter(raw)  # response from /filter
    elif isinstance(data, dict):
        return normalize_watchlist(raw)  # response from /graphql getWatchlist
    else:
        raise ValueError("data is not a list or a dict")


# handles /filter
def normalize_filter(raw: dict) -> list[tuple[str, dict]]:
    return [_normalize_filter_item(item) for item in raw.get("data", [])]


def _normalize_filter_item(item: dict) -> tuple[str, dict]:
    ticker = item.get("ticker_symbol")
    scores = item.get("score", {}).get("data")
    norm_keys = normalization.rename_keys(
        {
            "income": "dividend",
        }
    )
    scores = norm_keys(scores)
    return ticker, scores


def normalize_watchlist(raw):
    return [_normalize_watchlist_item(item) for item in raw.get("data", {}).get("Watchlist", {}).get("items", [])]


def _normalize_watchlist_item(item):
    company = item.get("company", {})
    ticker = company.get("tickerSymbol")
    scores = company.get("score")
    return ticker, scores


schema = {
    "value": int,
    "future": int,
    "past": int,
    "health": int,
    "dividend": int,
}
