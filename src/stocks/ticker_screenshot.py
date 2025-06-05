import re, datetime, asyncio, sys
from src.core.config import config
from src.core.proxies import random_proxy
from src.core.browser_session import browser_page
from playwright._impl._errors import TimeoutError, Error as PlaywrightError

output_dir = 'output/screenshots'
after_load_timeout = config.get('screenshot.browser.after_load_timeout')

def screenshot_tipranks(ticker: str, ticker_type: str):
    sync_screenshot_ticker('tipranks', ticker, f'https://www.tipranks.com/{ticker_type}/{ticker}/forecast')

def screenshot_tradingview(ticker: str):
    sync_screenshot_ticker('tradingview', ticker, f'https://tradingview.com/symbols/{ticker}/forecast/')

def screenshot_yahoo(ticker: str):
    sync_screenshot_ticker('yahoo', ticker, f'https://finance.yahoo.com/quote/{ticker}/analysis')

def screenshot_yahoo_br(ticker: str):
    sync_screenshot_ticker('yahoo', ticker, f'https://finance.yahoo.com/quote/{ticker}.sa/analysis')

def screenshot_investidor10(ticker: str):
    sync_screenshot_ticker('investidor10', ticker, f'https://investidor10.com.br/acoes/{ticker}/')

def screenshot_simplywall():
    sync_screenshot('simplywall.st', 'https://simplywall.st/stocks/br/top-gainers')

def sync_screenshot_ticker(site_name: str, ticker: str, url: str):
    asyncio.run(screenshot_ticker(site_name, ticker, url))

def sync_screenshot(site_name: str, url: str):
    asyncio.run(screenshot(site_name, url))

async def screenshot_ticker(site_name: str, ticker: str, url: str):
    await screenshot(f'{site_name}-{ticker}.png', url)

async def screenshot(key: str, url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'{key}-{timestamp}.png'
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
        print(f'   failed: {_error_type(e)}', file=sys.stderr)

def _error_type(e: Exception):
    if isinstance(e, TimeoutError):
        return type(e).__name__
    if isinstance(e, PlaywrightError):
        match = re.search(r'ERR_\w+', str(e))
        return match.group(0) if match else str(e)
    else:
        return str(e)
