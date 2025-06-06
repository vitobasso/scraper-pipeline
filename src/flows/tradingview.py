from src.flows.generic_screenshot import sync_screenshot
from src.flows import generic_extract
from src.flows.generic_screenshot_validate import validate as validate_screenshot


def flow():
    return {
        'name': 'investidor10',
        'screenshot': screenshot,
        'validate_screenshot': validate_screenshot,
        'extract_data': generic_extract.extract_analysis,
        'validate_data': lambda: None,
    }


def screenshot(ticker: str):
    sync_screenshot(f'tradingview-{ticker}', f'https://tradingview.com/symbols/{ticker}/forecast/')
