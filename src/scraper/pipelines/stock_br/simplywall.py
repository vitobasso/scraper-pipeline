import asyncio
import json
from pathlib import Path

from src.scraper.core import paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks.base import source_task
from src.scraper.core.tasks.normalization import normalize_json
from src.scraper.core.tasks.validation import validate_json
from src.scraper.services import browser
from src.scraper.services.proxies import random_proxy


def pipeline():
    return Pipeline.from_caller(
        tasks=[
            source_task(scrape),
            normalize_json(normalize, "validation"),
            validate_json(schema, "ready"),
        ],
    )


def scrape(pipe: Pipeline, ticker: str):
    url = f"https://simplywall.st/stock/bovespa/{ticker.lower()}"
    path = paths.for_pipe(pipe, ticker).output_file("normalization", "json")
    proxy = random_proxy(pipe)
    asyncio.run(_scrape(proxy, url, path, pipe, ticker))


async def _scrape(proxy: str, url: str, path: Path, pipe: Pipeline, ticker: str):
    print(f"scraping json, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with browser.new_page(proxy) as page:
            analysis_path = await _extract_href(page, url)
            analysis_url = f"https://simplywall.st{analysis_path}"
            await _intercept_company_summary(page, analysis_url, path)
    except Exception as e:
        log(browser.error_name(e), ticker, pipe)


async def _extract_href(page, url) -> str:
    await browser.goto(page, url)
    link = page.locator("a", has_text="Full Analysis").first
    return await link.get_attribute("href")


async def _intercept_company_summary(page, url: str, path: Path):
    match_request = lambda r: "/graphql" in r.url and "CompanySummary" in (r.request.post_data or "")
    data = await browser.expect_json_response(page, url, match_request)
    with open(path, "w") as f:
        json.dump(data, f)


normalize = lambda raw: raw.get("data", {}).get("Company", {}).get("score")

schema = {
    "value": int,
    "future": int,
    "past": int,
    "health": int,
    "dividend": int,
}
