from src.config import output_root
from src.scheduler import Pipeline, ticker_task, file_task
from src.flows.generic.screenshot import sync_screenshot
from src.flows.generic.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.flows.generic.extract_data import extract_json, input_dir as extract_data_input
from src.flows.generic.validate_data import input_dir as validate_data_input


name = 'investidor10'
output_dir = f'{output_root}/{name}'

def pipeline() -> Pipeline:
    return {
        'name': name,
        'tasks': [
            ticker_task(screenshot, output_dir),
            file_task(lambda path: validate_screenshot(path, output_dir), validate_screenshot_input(output_dir)),
            file_task(extract_data, extract_data_input(output_dir)),
            # file_task(lambda: None, validate_data_input(output_dir),
        ]
    }


def screenshot(ticker: str):
    sync_screenshot(output_dir, ticker, f'https://investidor10.com.br/acoes/{ticker}/')


def extract_data(image_path: str):
    prompt = f"""
    1. ticker e cotação
    2. rentabiliade
    3. indicadores fundamentalistas
    4. dados sobre a empresa
    5. informações sobre a empresa
    """
    extract_json(image_path, prompt, output_dir)
