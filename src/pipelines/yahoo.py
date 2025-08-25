import asyncio
import re
from pathlib import Path

from src.core import normalization
from src.core.logs import log
from src.core.scheduler import Pipeline
from src.core.screenshot import output_path
from src.core.tasks import extract_json, validate_json, source_task, normalize_json
from src.services.browser import page_goto, click, error_name
from src.services.proxies import random_proxy

name = 'yahoo'


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            source_task(name, screenshot),
            extract_json(name, prompt),
            validate_json(name, schema),
            normalize_json(name, normalize),
        ],
    )


def screenshot(ticker: str):
    url_ticker = f'{ticker}.sa' if re.match(r'\w{4}\d\d?', ticker) else ticker
    url = f'https://finance.yahoo.com/quote/{url_ticker}/analysis'
    path = output_path(ticker, name)
    asyncio.run(_screenshot(random_proxy(name), url, path, ticker))


async def _screenshot(proxy: str, url: str, path: Path, ticker: str):
    print(f'taking screenshot, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with page_goto(proxy, url, wait_until='domcontentloaded') as page:
            await _reject_cookies(page)
            await _dismiss_upgrade(page)
            await page.locator('div.cards-container').screenshot(path=path)
    except Exception as e:
        log(error_name(e), ticker, name)


async def _reject_cookies(page):
    try:
        await click(page, 'button[type="submit"][name="reject"]', timeout=1000)
        await page.wait_for_load_state('domcontentloaded')
    except:
        pass


async def _dismiss_upgrade(page):
    try:
        await click(page, '.dismiss', timeout=1000)
        await page.wait_for_load_state('domcontentloaded')
    except:
        pass


prompt = f"""
    1. analyst_rating (int values):
       - strong_buy
       - buy
       - hold
       - underperform
       - sell
        
        You should see a stacked bar chart. Use the latest (rightmost) month.
        The taller segments will have numbers. Use them when available [[priority]].
        For short segments without a number:
            - check the total number above the bar
            - get the remainder (subtract the numbers you already got fro taller segments)
            - check how many segments are missing a number (the short segments)
            - estimate their numbers based on relative height (distribute the remainder)
        
    2. price_forecast (float values)
       - min
       - avg
       - max
    """

schema = {
    'analyst_rating': ({
                           'strong_buy': int,
                           'buy': int,
                           'hold': int,
                           'underperform': int,
                           'sell': int,
                       }, None),
    'price_forecast': {
        'min': float,
        'avg': float,
        'max': float,
    }
}

normalize = normalization.rename_keys({
    "price_forecast": "forecast",
    "analyst_rating": "rating",
    "underperform": "sell",
    "sell": "strong_sell",
})
