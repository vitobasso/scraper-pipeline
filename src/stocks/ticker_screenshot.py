import datetime, asyncio, sys
import re

from src.core.proxies import random_proxy
from src.core.browser_session import browser_page
from src.core.config import config

output_dir = 'output/screenshots'
after_load_timeout = config.get('screenshot.browser.after_load_timeout')

def screenshot_tipranks(ticker: str, ticker_type: str):
    sync_screenshot('tipranks', ticker, f'https://www.tipranks.com/{ticker_type}/{ticker}/forecast')

def screenshot_tradingview(ticker: str):
    sync_screenshot('tradingview', ticker, f'https://tradingview.com/symbols/{ticker}/forecast/')

def screenshot_yahoo(ticker: str):
    sync_screenshot('yahoo', ticker, f'https://finance.yahoo.com/quote/{ticker}/analysis')

def screenshot_investidor10(ticker: str):
    sync_screenshot('investidor10', ticker, f'https://investidor10.com.br/acoes/{ticker}/')

def sync_screenshot(site_name: str, ticker: str, url: str):
    asyncio.run(screenshot(site_name, ticker, url))

async def screenshot(site_name: str, ticker: str, url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'{site_name}-{ticker}-{timestamp}.png'
    temp_path = f'{output_dir}/awaiting-validation/{filename}'
    proxy = random_proxy()
    print(f'taking screenshot, url: {url}, filename: {filename}, proxy: {proxy}')
    await _screenshot(proxy, url, temp_path)

async def _screenshot(proxy: str, url: str, path: str):
    try:
        async with browser_page(proxy, url, wait_until='load') as page:
            await page.wait_for_timeout(after_load_timeout)
            await page.screenshot(path=path, full_page=True, animations='disabled')
    except Exception as e:
        print(f'   failed: {_error_type(e)}', sys.stderr)

def _error_type(e: Exception):
    return re.match(r'(\w+) .*', type(e).__name__).group(1)
