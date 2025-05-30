from screenshot import take_screenshot
# from extract_layoutlm import extract
# from extract_textract import extract
from extract_googleai import extract
import datetime

def screenshot_tipranks(ticker: str):
    url = f"https://www.tipranks.com/etf/{ticker.lower()}/forecast"
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f"tipranks-{ticker}-{timestamp}.png"
    print(f'screenshot, url: {url}, filename: {filename}')
    take_screenshot(url, filename)

if __name__ == '__main__':
    screenshot_tipranks("qqq")
    # extract("screenshots/tipranks-qqq-2025-05-30T16-20-45.png")
