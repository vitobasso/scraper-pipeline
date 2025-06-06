import re, asyncio, sys
from src.core.browser_session import browser_page, click
from src.stocks.ticker_screenshot import _params, _error_type
from src.stocks.image_scrape import _extract_json

def screenshot_yahoo(ticker: str):
    url_ticker = f'{ticker}.sa' if re.match(r'\w{4}\d\d?', ticker) else ticker
    asyncio.run(_screenshot_yahoo(*_params(f'yahoo-{ticker}', f'https://finance.yahoo.com/quote/{url_ticker}/analysis')))

async def _screenshot_yahoo(proxy: str, url: str, path: str):
    print(f'taking screenshot, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with browser_page(proxy, url, wait_until='domcontentloaded') as page:
            await _reject_cookies(page)
            await page.locator('div.cards-container').screenshot(path=path)
            # await page.screenshot(path=path, full_page=True)
    except Exception as e:
        print(f'failed: {_error_type(e)}', file=sys.stderr)

async def _reject_cookies(page):
    try:
        await click(page, 'button[type="submit"][name="reject"]', timeout=1000)
        await page.wait_for_load_state('domcontentloaded')
    except Exception as e:
        pass

def extract_analysis(path: str):
    prompt = f"""
    1. analyst rating (int values):
       - strong buy (optional)
       - buy
       - hold
       - sell
       - strong sell (optional)
        
        You should see a stacked bar chart. Use the latest (rightmost) month.
        The taller segments will have numbers. Use them when available [[priority]].
        For short segments without a number:
            - check the total number above the bar
            - get the remainder (subtract the numbers you already got fro taller segments)
            - check how many segments are missing a number (the short segments)
            - estimate their numbers based on relative height (distribute the remainder)
        
    2. price forecast (float values)
       - min (aka low)
       - avg
       - max (aka high)
    """
    _extract_json(path, prompt)