from src.flows.generic_extract import _extract_json
from src.flows.generic_screenshot import sync_screenshot


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
    _extract_json(image_path, prompt)
