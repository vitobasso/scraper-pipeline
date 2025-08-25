import asyncio
import json
from pathlib import Path

from src.core import paths
from src.core.logs import log
from src.core.scheduler import Pipeline
from src.core.tasks import normalize_json, source_task, validate_json
from src.core.util import timestamp
from src.services import browser
from src.services.proxies import random_proxy

name = "simplywall"


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            source_task(name, scrape),
            normalize_json(name, normalize, "validation"),
            validate_json(name, schema, "ready"),
        ],
    )


def scrape(ticker):
    url = f"https://simplywall.st/stock/bovespa/{ticker.lower()}"
    path = paths.stage_dir_for(ticker, name, "normalization") / f"{timestamp()}.json"
    proxy = random_proxy(name)
    asyncio.run(_scrape(proxy, url, path, ticker))


async def _scrape(proxy: str, url: str, path: Path, ticker: str):
    print(f"scraping json, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with browser.new_page(proxy) as page:
            analysis_path = await _extract_href(page, url)
            analysis_url = f"https://simplywall.st{analysis_path}"
            await _intercept_company_summary(page, analysis_url, path)
    except Exception as e:
        log(browser.error_name(e), ticker, name)


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
