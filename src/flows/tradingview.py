import asyncio, sys
from src.scheduler import Pipeline, ticker_task, file_task
from src.core.browser_session import browser_page, error_name
from src.flows.generic.screenshot import params
from src.flows.generic.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.flows.generic.extract_data import extract_json, input_dir as extract_data_input
from src.flows.generic.validate_data import validate, input_dir as validate_data_input


def pipeline() -> Pipeline:
    name = 'tradingview'
    output_dirs = [validate_screenshot_input, extract_data_input, validate_data_input]#, completed_dir]
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
    asyncio.run(_screenshot(*params(f'tradingview-{ticker}', f'https://tradingview.com/symbols/{ticker}/forecast')))


async def _screenshot(proxy: str, url: str, path: str):
    print(f'taking screenshot, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with browser_page(proxy, url, wait_until='domcontentloaded') as page:
            locator = common_ancestor(page, ['Price target', 'Analyst rating'])
            await locator.screenshot(path=path)
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)


def common_ancestor(page, texts: list[str]):
    children = ' and '.join([_xpath_contains(text) for text in texts])
    return page.locator(f"""xpath=//*[{children}]""").last


def _xpath_contains(text: str):
    return f".//text()[contains(., '{text}')]"


def extract_data(image_path: str):
    prompt = f"""
    1. analyst_rating (int values):
       - strong_buy
       - buy
       - hold
       - sell
       - strong_sell
    2. price_forecast (float values)
       - min
       - avg
       - max
    """
    extract_json(image_path, prompt)


def validate_data(path: str):
    schema = {
        'analyst_rating': {
            'strong_buy': int,
            'buy': int,
            'hold': int,
            'sell': int,
            'strong_sell': int,
        },
        'price_forecast': {
            'min': float,
            'avg': float,
            'max': float,
        }
    }
    validate(path, schema)
