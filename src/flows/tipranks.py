from src.config import output_root
from src.flows.generic.screenshot import sync_screenshot
from src.scheduler import Pipeline, ticker_task, file_task
from src.flows.generic.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.flows.generic.extract_data import extract_json, input_dir as extract_data_input
from src.flows.generic.validate_data import validate, input_dir as validate_data_input

name = 'tipranks'
output_dir = f'{output_root}/{name}'

def pipeline() -> Pipeline:
    return { #TODO input must be us stocks
        'name': name,
        'tasks': [
            ticker_task(screenshot, output_dir),
            file_task(lambda path: validate_screenshot(path, output_dir), validate_screenshot_input(output_dir)),
            file_task(extract_data, extract_data_input(output_dir)),
            file_task(validate_data, validate_data_input(output_dir)),
        ]
    }


def screenshot(ticker: str):
    sync_screenshot(output_dir, ticker, f'https://www.tipranks.com/stocks/{ticker}/forecast')


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
    extract_json(image_path, prompt, output_dir)


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
    validate(path, schema, output_dir)
