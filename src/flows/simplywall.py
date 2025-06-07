import datetime, asyncio, sys, json
from src.config import output_dir
from src.core.util import mkdir
from src.core.proxies import random_proxy
from src.core.browser_session import browser_page2, error_name, load_timeout
from src.flows.generic.validate_screenshot import validate as validate_screenshot
from src.flows.generic.extract_data import extract
from src.flows.generic.validate_data import validate

download_dir = mkdir(f'{output_dir}/downloads/awaiting-extraction')

def flow():
    return {
        'name': 'simplywall',
        'screenshot': lambda: None, #TODO
        'validate_screenshot': validate_screenshot,
        'extract_data': extract_data,
        'validate_data': validate_data,
    }


def scrape():
    asyncio.run(_scrape(*params(f'simplywall', 'https://simplywall.st/stocks/br/top-gainers')))


async def _scrape(proxy: str, url: str, path: str):
    print(f'scraping, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with browser_page2(proxy) as page:
            async with page.expect_response(lambda r: "api/grid/filter" in r.url) as response_info:
                await page.goto(url, timeout=load_timeout, wait_until='domcontentloaded')
            response = await response_info.value
            data = await response.json()
            with open(path, 'w') as f:
                json.dump(data, f)
            #TODO pagination
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)


def params(key: str, url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'{key}-{timestamp}.json'
    output_path = f'{download_dir}/{filename}'
    proxy = random_proxy()
    return proxy, url, output_path


# TODO not needed for scraped json
def extract_data(image_path: str):
    prompt = f"""
    Extract the values from each radar chart shown. Each chart has 5 axes with values ranging from 0 to 6.

    Return a list of JSON objects — one per radar chart — in top-to-bottom order.
    Each object must include:
    - "ticker": (string)
    - 5 numeric fields corresponding to the axes, labeled in clockwise order starting from the top:
        - "value"
        - "future"
        - "past"
        - "health"
        - "dividend"
    Use this format:
    [
      {"ticker": "BBAS3", "value": 3, "future": 2, "past": 1, "health": 4, "dividend": 3},
      ...
    ]
    
    If you can’t read a chart, include "error": "unreadable" instead of the axis values. 
    Avoid any markdown formatting or backticks.
    """
    extract(image_path, prompt)


def validate_data(path: str):
    schema = [
        {
            'ticker': str,
            'value': int,
            'future': int,
            'past': int,
            'health': int,
            'dividend': int,
        }
    ]
    validate(path, schema)
