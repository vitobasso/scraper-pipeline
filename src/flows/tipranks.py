from src.flows.generic.screenshot import sync_screenshot
from src.scheduler import Pipeline, ticker_task, file_task, completed_dir
from src.flows.generic.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.flows.generic.extract_data import extract_json, input_dir as extract_data_input
from src.flows.generic.validate_data import validate, input_dir as validate_data_input


def pipeline() -> Pipeline:
    name = 'tipranks'
    output_dirs = [validate_screenshot_input, extract_data_input, validate_data_input, completed_dir]
    return {
        'name': name,
        'tasks': [
            ticker_task(lambda ticker: screenshot(ticker, 'stocks'), output_dirs, name),
            file_task(validate_screenshot, validate_screenshot_input, name),
            file_task(extract_data, extract_data_input, name),
            file_task(validate_data, validate_data_input, name),
        ]
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
