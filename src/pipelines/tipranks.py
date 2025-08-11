from src.config import output_root
from src.common.screenshot import ss_common_ancestor
from src.scheduler import Pipeline, line_task, file_task
from src.common.util import mkdir
from src.common.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.common.extract_data import extract_json, input_dir as extract_data_input
from src.common.validate_data import validate_schema, input_dir as validate_data_input

name = 'tipranks'
output_dir = mkdir(f'{output_root}/{name}')


def pipeline(input_path: str):
    return Pipeline(
        name=name,
        tasks=[
            line_task(screenshot, input_path, output_dir),
            file_task(lambda path: validate_screenshot(path, output_dir), validate_screenshot_input(output_dir)),
            file_task(extract_data, extract_data_input(output_dir)),
            file_task(validate_data, validate_data_input(output_dir)),
        ]
    )


def screenshot(ticker: str):
    ss_common_ancestor(ticker, f'https://www.tipranks.com/stocks/{ticker}/forecast',
                       ['Month Forecast', 'Analyst Ratings'], output_dir, name)


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
    extract_json(image_path, prompt, output_dir, name)


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
    validate_schema(path, schema, output_dir)
