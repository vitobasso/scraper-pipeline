import os, re, asyncio, sys, json
from src.config import output_dir
from src.core.browser_session import browser_page, click, error_name
from src.core.util import mkdir, all_files, get_ticker
from src.flows.generic_screenshot import params
from src.flows.generic_screenshot_validate import validate as validate_screenshot
from src.flows.generic_extract import _extract_json

data_dir = f'{output_dir}/data'
valid_data_dir = mkdir(f'{data_dir}/ready')
invalid_data_dir = mkdir(f'{data_dir}/failed-validation')

def flow():
    return {
        'name': 'yahoo',
        'screenshot': screenshot,
        'validate_screenshot': validate_screenshot,
        'extract_data': extract_data,
        'validate_data': validate_data,
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
            # await page.screenshot(path=path, full_page=True)
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
    _extract_json(path, prompt)

def validate_data(path):
    dest_dir = valid_data_dir if _validate_data(path) else invalid_data_dir
    dest_path = f'{dest_dir}/{os.path.basename(path)}'
    os.rename(path, dest_path)

def _validate_data(path):
    try:
        with open(path) as f:
            data = json.load(f)
        return all(k in data for k in ("analyst_rating", "price_forecast"))
    except:
        return False

def compile_data():
    return [_compile_row(path) for path in all_files(valid_data_dir, 'yahoo')]

def _compile_row(path):
    ticker = get_ticker(path)
    with open(path) as file:
        data = json.load(file)
        analyst_rating = data.get('analyst_rating') or {}
        price_forecast = data.get('price_forecast') or {}
        return [ticker, None, None, None, None, None, analyst_rating.get('strong_buy'), analyst_rating.get('buy'),
                analyst_rating.get('hold'), analyst_rating.get('sell'), analyst_rating.get('strong_sell'), #TODO underperform and sell
                price_forecast.get('min'), price_forecast.get('avg'), price_forecast.get('max')]
