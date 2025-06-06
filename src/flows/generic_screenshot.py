import datetime, asyncio, sys
from src.core.config import config
from src.core.proxies import random_proxy
from src.core.browser_session import browser_page, error_type

output_dir = 'output/screenshots'
after_load_timeout = config.get('screenshot.browser.after_load_timeout')

def screenshot_tipranks(ticker: str, ticker_type: str):
    sync_screenshot(f'tipranks-{ticker}', f'https://www.tipranks.com/{ticker_type}/{ticker}/forecast')

def screenshot_tradingview(ticker: str):
    sync_screenshot(f'tradingview-{ticker}', f'https://tradingview.com/symbols/{ticker}/forecast/')

def screenshot_simplywall():
    sync_screenshot('simplywall.st', 'https://simplywall.st/stocks/br/top-gainers')

def sync_screenshot(key: str, url: str):
    asyncio.run(_screenshot(*params(key, url)))

def params(key: str, url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'{key}-{timestamp}.png'
    output_path = f'{output_dir}/awaiting-validation/{filename}'
    proxy = random_proxy()
    return proxy, url, output_path

async def _screenshot(proxy: str, url: str, path: str):
    print(f'taking screenshot, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with browser_page(proxy, url, wait_until='load') as page:
            await page.wait_for_timeout(after_load_timeout)
            await page.screenshot(path=path, full_page=True, animations='disabled')
    except Exception as e:
        print(f'failed: {error_type(e)}', file=sys.stderr)
