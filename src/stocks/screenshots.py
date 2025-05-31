import csv, datetime, asyncio
from src.core import proxies
from src.core.screenshot import screenshot

parallel = 10

def run_tasks():
    with open('input/tickers.csv', 'r') as file:
        tickers = [record for record in csv.DictReader(file, fieldnames=['ticker', 'type'])]
    asyncio.run(_run_tasks(tickers))

async def _run_tasks(tickers):
    tasks = [_screenshot_tradingview(tickers[i]['ticker']) for i in range(parallel)]
    return await asyncio.gather(*tasks)

async def _run_task(task):
    return task()

async def _screenshot_tipranks(ticker: str, ticker_type: str):
    await _screenshot_template('tipranks', ticker, f'https://www.tipranks.com/{ticker_type}/{ticker}/forecast')

async def _screenshot_tradingview(ticker: str):
    await _screenshot_template('tradingview', ticker, f'https://tradingview.com/symbols/{ticker}/forecast/')

async def _screenshot_template(site: str, ticker: str, url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'{site}-{ticker}-{timestamp}.png'
    print(f'taking screenshot, url: {url}, filename: {filename}')
    await proxies.run_task(lambda proxy: screenshot(url, filename, proxy))