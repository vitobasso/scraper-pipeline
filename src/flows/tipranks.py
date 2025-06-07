from src.flows.generic.screenshot import sync_screenshot
from src.flows.generic.validate_screenshot import validate as validate_screenshot
from src.flows.generic.extract_data import extract_json
from src.flows.generic.validate_data import validate


def flow():
    return {
        'name': 'tipranks',
        'screenshot': lambda ticker: screenshot(ticker, 'stocks'),
        'validate_screenshot': validate_screenshot,
        'extract_data': extract_data,
        'validate_data': validate_data,
    }


def screenshot(ticker: str, ticker_type: str):
    sync_screenshot(f'tipranks-{ticker}', f'https://www.tipranks.com/{ticker_type}/{ticker}/forecast')


def extract_data(image_path: str):
    prompt = f"""
    1. analyst_rating (int values):
       - buy
       - hold
       - sell
    2. price_forecast (float values)
       - min (aka low)
       - avg
       - max (aka high)
    """
    extract_json(image_path, prompt)


def validate_data(path: str):
    schema = {
        'analyst_rating': {
           'buy': int,
           'hold': int,
           'sell': int,
        },
        'price_forecast': {
            'min': float,
            'avg': float,
            'max': float,
        }
    }
    validate(path, schema)
