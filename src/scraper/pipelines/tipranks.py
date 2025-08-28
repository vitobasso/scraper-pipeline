from src.scraper.core import normalization
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.screenshot import ss_common_ancestor
from src.scraper.core.tasks import extract_json, normalize_json, source_task, validate_json

name = "tipranks"


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            source_task(name, screenshot),
            extract_json(name, prompt),
            validate_json(name, schema),
            normalize_json(name, normalize),
        ],
    )


def screenshot(ticker: str):
    ss_common_ancestor(
        ticker, name, f"https://www.tipranks.com/stocks/{ticker}/forecast", ["Month Forecast", "Analyst Ratings"]
    )


prompt = """
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
    "analyst_rating": {
        "buy": int,
        "hold": int,
        "sell": int,
    },
    "price_forecast": {
        "min": float,
        "avg": float,
        "max": float,
    },
}

normalize = normalization.rename_keys(
    {
        "price_forecast": "forecast",
        "analyst_rating": "rating",
    }
)
