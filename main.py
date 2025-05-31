import proxies
from screenshot import take_screenshot
from extract_googleai import extract
import datetime

def screenshot_tipranks(ticker: str):
    screenshot_template('tipranks', ticker, f'https://www.tipranks.com/etf/{ticker.lower()}/forecast')

def screenshot_tradingview(ticker: str):
    screenshot_template('tradingview', ticker, f'https://tradingview.com/symbols/{ticker.upper()}/forecast/')

def screenshot_template(site: str, ticker: str, url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'{site}-{ticker}-{timestamp}.png'
    print(f'taking screenshot, url: {url}, filename: {filename}')
    proxies.run_task(lambda proxy: take_screenshot(url, filename, proxy))

if __name__ == '__main__':
    for i in range(10):
        screenshot_tipranks('qqq')
        screenshot_tradingview('BMFBOVESPA-PETR4')
    # extract("screenshots/tradingview-BMFBOVESPA-PETR4-20250530T184949.png")
    # extract("screenshots/tipranks-qqq-20250530T180430.png")
