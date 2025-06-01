import os, csv, datetime, asyncio
from src.core import proxies
from src.core.screenshot import screenshot
from src.stocks.stocks_image_validate import validate
from src.core.config import config

screenshot_dir = config.get('screenshot.path')
parallel = config.get('screenshot.parallel')

def run_tasks():
    with open('input/tickers.csv', 'r') as file:
        tickers = [record for record in csv.DictReader(file, fieldnames=['ticker', 'type'])]
    asyncio.run(_run_tasks(tickers))

async def _run_tasks(tickers):
    # tasks = [_screenshot_tradingview(tickers[i]['ticker']) for i in range(parallel)]
    # tasks = [_screenshot_tipranks(tickers[i]['ticker'], tickers[i]['type']) for i in range(parallel)]
    # tasks = [_screenshot_yahoo(tickers[i]['ticker']) for i in range(parallel)]
    tasks = [_screenshot_investidor10(tickers[i]['ticker']) for i in range(parallel)]
    return await asyncio.gather(*tasks)

async def _run_task(task):
    return task()

async def _screenshot_tipranks(ticker: str, ticker_type: str):
    await _screenshot('tipranks', ticker, f'https://www.tipranks.com/{ticker_type}/{ticker}/forecast')

async def _screenshot_tradingview(ticker: str):
    await _screenshot('tradingview', ticker, f'https://tradingview.com/symbols/{ticker}/forecast/')

async def _screenshot_yahoo(ticker: str):
    await _screenshot('yahoo', ticker, f'https://finance.yahoo.com/quote/{ticker}/analysis')

async def _screenshot_investidor10(ticker: str):
    await _screenshot('investidor10', ticker, f'https://investidor10.com.br/acoes/{ticker}/')

async def _screenshot(site: str, ticker: str, url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'{site}-{ticker}-{timestamp}.png'
    print(f'taking screenshot, url: {url}, filename: {filename}')
    temp_path = f'{screenshot_dir}/temp/{filename}'
    valid_path = f'{screenshot_dir}/valid/{filename}'
    invalid_path = f'{screenshot_dir}/invalid/{filename}'
    await proxies.run_task(lambda proxy: screenshot(url, temp_path, proxy))
    if os.path.exists(temp_path):
        dest_path = valid_path if validate(temp_path) else invalid_path
        _move_file(temp_path, dest_path)

def _move_file(temp_path, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    os.rename(temp_path, dest_path)