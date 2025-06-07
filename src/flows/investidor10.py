from src.flows.generic.extract_data import extract_json
from src.flows.generic.screenshot import sync_screenshot
from src.flows.generic.validate_screenshot import validate as validate_screenshot


def flow():
    return {
        'name': 'investidor10',
        'screenshot': screenshot,
        'validate_screenshot': validate_screenshot,
        'extract_data': extract_data,
        'validate_data': lambda: None,
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
