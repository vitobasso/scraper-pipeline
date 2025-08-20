from src.core.scheduler import Pipeline
from src.core.screenshot import ss_full_page
from src.core.tasks import validate_json, extract_json, source_task

name = 'investidor10'


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            source_task(name, screenshot),
            extract_json(name, prompt),
            validate_json(name, schema),
        ],
    )


def screenshot(ticker: str):
    ss_full_page(ticker, name, f'https://investidor10.com.br/acoes/{ticker}/')


prompt = f"""
    1. ticker e cotação
    2. rentabiliade
    3. indicadores fundamentalistas
    4. dados sobre a empresa
    5. informações sobre a empresa
    
    All keys should be lower_snake_case in portuguese without special characters.
    """

schema = {
    'informacoes_sobre_a_empresa': {
        'setor': str,
        'segmento': str,
    }
}
