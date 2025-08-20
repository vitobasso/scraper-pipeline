from src.core.scheduler import Pipeline
from src.core.screenshot import ss_common_ancestor
from src.core.tasks import validate_json, extract_json, source_task

name = 'tradingview'


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
    ss_common_ancestor(ticker, name, f'https://tradingview.com/symbols/{ticker}/forecast',
                       ['Price target', 'Analyst rating'])


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
