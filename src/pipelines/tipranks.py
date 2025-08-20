from src.core.screenshot import ss_common_ancestor
from src.core.tasks import validate_json, extract_json, source_task
from src.core.scheduler import Pipeline

name = 'tipranks'


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            source_task(name, screenshot),
            extract_json(name, prompt),
            validate_json(name, schema),
        ]
    )


def screenshot(ticker: str):
    ss_common_ancestor(ticker, name, f'https://www.tipranks.com/stocks/{ticker}/forecast',
                       ['Month Forecast', 'Analyst Ratings'])


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
