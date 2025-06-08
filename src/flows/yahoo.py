import re, asyncio, sys, json
from src.scheduler import Pipeline, ticker_task, file_task, completed_dir
from src.core.browser_session import browser_page, click, error_name
from src.core.util import all_files, get_ticker
from src.flows.generic.screenshot import params
from src.flows.generic.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.flows.generic.extract_data import extract_json, input_dir as extract_data_input
from src.flows.generic.validate_data import valid_data_dir, validate, input_dir as validate_data_input


def pipeline() -> Pipeline:
    name = 'yahoo'
    output_dirs = [validate_screenshot_input, extract_data_input, validate_data_input, completed_dir]
    return {
        'name': name,
        'tasks': [
            ticker_task(screenshot, output_dirs, name),
            file_task(validate_screenshot, validate_screenshot_input, name),
            file_task(extract_data, extract_data_input, name),
            file_task(validate_data, validate_data_input, name),
        ]
    }


def screenshot(ticker: str):
    url_ticker = f'{ticker}.sa' if re.match(r'\w{4}\d\d?', ticker) else ticker
    asyncio.run(_screenshot(*params(f'yahoo-{ticker}', f'https://finance.yahoo.com/quote/{url_ticker}/analysis')))


async def _screenshot(proxy: str, url: str, path: str):
    print(f'taking screenshot, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with browser_page(proxy, url, wait_until='domcontentloaded') as page:
            await _reject_cookies(page)
            await _dismiss_upgrade(page)
            await page.locator('div.cards-container').screenshot(path=path)
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)


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
    extract_json(path, prompt)


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
    validate(path, schema)


def compile_data():
    return [_compile_row(path) for path in all_files(valid_data_dir, 'yahoo')]


def _compile_row(path):
    ticker = get_ticker(path)
    with open(path) as file:
        data = json.load(file)
        analyst_rating = data.get('analyst_rating') or {}
        price_forecast = data.get('price_forecast') or {}
        return [ticker, None, None, None, None, None, analyst_rating.get('strong_buy'), analyst_rating.get('buy'),
                analyst_rating.get('hold'), analyst_rating.get('underperform'), analyst_rating.get('sell'),
                price_forecast.get('min'), price_forecast.get('avg'), price_forecast.get('max')]
