# from src.stocks import stocks_screenshot
# from src.stocks.stocks_image_scrape import extract_analysis
# from src.stocks.stocks_image_scrape import extract_fundamentals
from src.stocks.download_statusinvest import download
import src.core.proxies as proxies
import asyncio, datetime

def download_statusinvest():
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    path = f'output/downloads/statusinvest-{timestamp}.csv'
    asyncio.run(download(path, proxies.pick()))

if __name__ == '__main__':
    # stocks_screenshot.run_tasks()
    download_statusinvest()
    # extract_analysis("output/screenshots/valid/tradingview-BMFBOVESPA-PETR4-20250530T184949.png")
    # extract_analysis("output/screenshots/valid/tipranks-qqq-20250530T180430.png")
    # extract_fundamentals("output/screenshots/valid/investidor10-bbas3-20250601T155718.png")

