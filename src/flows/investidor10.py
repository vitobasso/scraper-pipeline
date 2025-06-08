from src.scheduler import Pipeline, ticker_task, file_task
from src.flows.generic.screenshot import sync_screenshot
from src.flows.generic.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.flows.generic.extract_data import extract_json, input_dir as extract_data_input
from src.flows.generic.validate_data import input_dir as validate_data_input


def pipeline() -> Pipeline:
    name = 'investidor10'
    output_dirs = [validate_screenshot_input, extract_data_input, validate_data_input]#, completed_dir]
    return {
        'name': name,
        'tasks': [
            ticker_task(screenshot, output_dirs, name),
            file_task(validate_screenshot, validate_screenshot_input, name),
            file_task(extract_data, extract_data_input, name),
            # file_task(lambda: None, validate_data_input, name),
        ]
    }


def screenshot(ticker: str):
    sync_screenshot(f'investidor10-{ticker}', f'https://investidor10.com.br/acoes/{ticker}/')


def extract_data(image_path: str):
    prompt = f"""
    1. ticker e cotação
    2. rentabiliade
    3. indicadores fundamentalistas
    4. dados sobre a empresa
    5. informações sobre a empresa
    """
    extract_json(image_path, prompt)
