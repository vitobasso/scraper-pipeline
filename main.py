from screenshot import take_screenshot
from extract_googleai import extract
import datetime

def screenshot_tipranks(ticker: str):
    url = f"https://www.tipranks.com/etf/{ticker.lower()}/forecast"
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f"tipranks-{ticker}-{timestamp}.png"
    print(f'screenshot, url: {url}, filename: {filename}')
    take_screenshot(url, filename)

def screenshot_tradingview(ticker: str):
    url = f"https://tradingview.com/symbols/{ticker.upper()}/forecast/"
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f"tradingview-{ticker}-{timestamp}.png"
    print(f'screenshot, url: {url}, filename: {filename}')
    take_screenshot(url, filename)

if __name__ == '__main__':
    # screenshot_tipranks("qqq")
    # screenshot_tradingview("BMFBOVESPA-PETR4")
    extract("screenshots/tradingview-BMFBOVESPA-PETR4-20250530T184949.png")
    # extract("screenshots/tipranks-qqq-20250530T180430.png")
