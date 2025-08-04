import re, asyncio

from src.common.logs import log
from src.common.spreadsheet import json_to_spreadsheet
from src.config import output_root
from src.scheduler import Pipeline, line_task, file_task, line_progress
from src.services.browser import page_goto, click, error_name
from src.common.util import mkdir
from src.services.proxies import random_proxy
from src.common.screenshot import output_path
from src.common.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.common.extract_data import extract_json, input_dir as extract_data_input
from src.common.validate_data import valid_data_dir, validate_schema, input_dir as validate_data_input

name = 'yahoo'
output_dir = mkdir(f'{output_root}/{name}')
completed_dir = valid_data_dir(output_dir)


def pipeline(input_path: str):
    return Pipeline(
        name=name,
        tasks=[
            line_task(screenshot, input_path, output_dir),
            file_task(lambda path: validate_screenshot(path, output_dir), validate_screenshot_input(output_dir)),
            file_task(extract_data, extract_data_input(output_dir)),
            file_task(validate_data, validate_data_input(output_dir)),
        ],
        progress=line_progress(input_path, output_dir)
    )


def screenshot(ticker: str):
    url_ticker = f'{ticker}.sa' if re.match(r'\w{4}\d\d?', ticker) else ticker
    url = f'https://finance.yahoo.com/quote/{url_ticker}/analysis'
    path = output_path(output_dir, ticker)
    asyncio.run(_screenshot(random_proxy(), url, path, ticker))


async def _screenshot(proxy: str, url: str, path: str, ticker: str):
    print(f'taking screenshot, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with page_goto(proxy, url, wait_until='domcontentloaded') as page:
            await _reject_cookies(page)
            await _dismiss_upgrade(page)
            await page.locator('div.cards-container').screenshot(path=path)
    except Exception as e:
        log(error_name(e), name, ticker)


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


def extract_data(path: str):
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
    extract_json(path, prompt, output_dir)


def validate_data(path: str):
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
    validate_schema(path, schema, output_dir)


def to_spreadsheet():
    return json_to_spreadsheet(completed_dir)
