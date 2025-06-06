import asyncio, sys
from src.core.browser_session import browser_page, click, error_name
from src.flows.generic_screenshot import params
from src.flows.generic_screenshot_validate import validate as validate_screenshot
from src.flows.generic_extract import extract_json


def flow():
    return {
        'name': 'investidor10',
        'screenshot': screenshot,
        'validate_screenshot': validate_screenshot,
        'extract_data': extract_data,
        'validate_data': lambda: None,
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
    1. analyst_rating (int):
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