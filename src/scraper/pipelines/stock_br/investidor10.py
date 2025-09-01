import re

from src.scraper.core import normalization
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.screenshot import ss_full_page
from src.scraper.core.tasks import extract_json, normalize_json, source_task, validate_json


def pipeline():
    return Pipeline.from_caller(
        tasks=[
            source_task(screenshot),
            extract_json(prompt),
            validate_json(schema),
            normalize_json(normalize),
        ],
    )


def screenshot(pipe: Pipeline, ticker: str):
    ss_full_page(ticker, pipe, f"https://investidor10.com.br/acoes/{ticker}/")


prompt = """
    1. ticker e cotação
    2. rentabiliade
    3. indicadores fundamentalistas
    4. dados sobre a empresa
    5. informações sobre a empresa

    All keys should be lower_snake_case in portuguese without special characters.
    Replace "/" with "_". E.g.: "P/L" becomes "p_l"
    """

schema = {
    "informacoes_sobre_a_empresa": {
        "setor": str,
        "segmento": str,
    }
}


def normalize(data):
    rename_keys = normalization.rename_keys(
        {
            "indicadores_fundamentalistas": "fundamentos",
            "dados_sobre_a_empresa": "cadastral",
            "informacoes_sobre_a_empresa": "financeiro",
            "rentabilidade": "rent",
            "rentabilidade_nominal": "nominal",
            "rentabilidade_real": "real",
        }
    )

    norm_values = normalization.traverse_values(normalization.value)

    bil = normalization.pipe(_parse_magnitude, lambda v: v / 1_000_000_000.0)
    mil = normalization.pipe(_parse_magnitude, lambda v: v / 1_000_000.0)
    parse_magnitude = normalization.traverse_dict(
        {
            "valor_de_mercado": bil,
            "valor_de_firma": bil,
            "patrimonio_liquido": bil,
            "numero_total_de_papeis": bil,
            "ativos": bil,
            "ativo_circulante": bil,
            "divida_bruta": bil,
            "divida_liquida": bil,
            "disponibilidade": bil,
            "liquidez_media_diaria": mil,
        }
    )
    return normalization.pipe(rename_keys, norm_values, parse_magnitude)(data)


def _parse_magnitude(v):
    """Parses numbers in (Bilhão/Bilhões, Milhão/Milhões)"""

    unit_re = re.compile(r"\s*(bilh(?:ões|ao|ão|oes)?|milh(?:ões|ao|ão|oes)?)\b", re.IGNORECASE)

    if not isinstance(v, str):
        return v
    lower = v.lower()
    unit = "bi" if "bilh" in lower else ("mi" if "milh" in lower else None)
    if not unit:
        return v
    stripped = unit_re.sub("", v)
    num = normalization.value(stripped)
    if not isinstance(num, int | float):
        return v
    if unit == "mi":
        return num * 1_000_000.0
    if unit == "bi":
        return num * 1_000_000_000.0
    return v
