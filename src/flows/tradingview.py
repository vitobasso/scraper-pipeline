from src.config import output_root
from src.flows.generic.extract_data import extract_json, input_dir as extract_data_input
from src.flows.generic.screenshot import ss_common_ancestor
from src.flows.generic.validate_data import validate, input_dir as validate_data_input
from src.flows.generic.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.scheduler import Pipeline, line_task, file_task

name = 'tradingview'
output_dir = f'{output_root}/{name}'


def pipeline(input_path: str) -> Pipeline:
    return {
        'name': name,
        'tasks': [
            line_task(screenshot, input_path, output_dir),
            file_task(lambda path: validate_screenshot(path, output_dir), validate_screenshot_input(output_dir)),
            file_task(extract_data, extract_data_input(output_dir)),
            file_task(validate_data, validate_data_input(output_dir)),
        ]
    }


def screenshot(ticker: str):
    ss_common_ancestor(ticker, f'https://tradingview.com/symbols/{ticker}/forecast',
                       ['Price target', 'Analyst rating'], output_dir)


def extract_data(image_path: str):
    prompt = f"""
    1. analyst_rating (int values):
       - strong_buy
       - buy
       - hold
       - sell
       - strong_sell
    2. price_forecast (float values)
       - min
       - avg
       - max
    """
    extract_json(image_path, prompt, output_dir)


def validate_data(path: str):
    schema = {
        'analyst_rating': {
            'strong_buy': int,
            'buy': int,
            'hold': int,
            'sell': int,
            'strong_sell': int,
        },
        'price_forecast': {
            'min': float,
            'avg': float,
            'max': float,
        }
    }
    validate(path, schema, output_dir)
