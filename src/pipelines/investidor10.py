from src.config import output_root
from src.scheduler import Pipeline, line_task, file_task, line_progress
from src.common.util import mkdir
from src.common.screenshot import ss_full_page
from src.common.validate_screenshot import validate_screenshot, input_dir as validate_screenshot_input
from src.common.extract_data import extract_json, input_dir as extract_data_input
from src.common.validate_data import valid_data_dir, validate_schema, input_dir as validate_data_input

name = 'investidor10'
output_dir = mkdir(f'{output_root}/{name}')
completed_dir = valid_data_dir(output_dir)


def pipeline(input_path: str):
    return Pipeline(
        name=name,
        tasks=[
            line_task(screenshot, input_path, output_dir),
            file_task(lambda path: validate_screenshot(path, output_dir),
                      validate_screenshot_input(output_dir)),
            file_task(extract_data, extract_data_input(output_dir)),
            file_task(validate_data, validate_data_input(output_dir)),
        ],
        progress=line_progress(input_path, output_dir)
    )


def screenshot(ticker: str):
    ss_full_page(ticker, f'https://investidor10.com.br/acoes/{ticker}/', output_dir, name)


def extract_data(image_path: str):
    prompt = f"""
    1. ticker e cotação
    2. rentabiliade
    3. indicadores fundamentalistas
    4. dados sobre a empresa
    5. informações sobre a empresa
    
    All keys should be lower_snake_case in portuguese without special characters.
    """
    extract_json(image_path, prompt, output_dir, name)


def validate_data(path: str):
    schema = {
        'informacoes_sobre_a_empresa': {
            'setor': str,
            'segmento': str,
        }
    }
    validate_schema(path, schema, output_dir)

