from src.config import output_root
from src.common.util import mkdir
from src.common.extract_data import extract_json, input_dir as extract_data_input
from src.common.screenshot import ss_common_ancestor
from src.common.validate_data import validate_schema, input_dir as validate_data_input, valid_data_dir
from src.common.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.scheduler import Pipeline, line_task, file_task, line_progress

name = 'tradingview'
output_dir = mkdir(f'{output_root}/{name}')
completed_dir = valid_data_dir(output_dir)


def pipeline(input_path: str):
    return Pipeline(
        name=name,
        tasks=[
            line_task(screenshot, input_path, output_dir),
            file_task(lambda path: validate_screenshot(path, output_dir), validate_screenshot_input(output_dir)),
            file_task(extract_data, extract_data_input(output_dir)),
            file_task(validate_data, validate_data_input(output_dir)),
        ],
        progress=line_progress(input_path, output_dir)
    )


def screenshot(ticker: str):
    ss_common_ancestor(ticker, f'https://tradingview.com/symbols/{ticker}/forecast',
                       ['Price target', 'Analyst rating'], output_dir, name)


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
    validate_schema(path, schema, output_dir)
