from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import normalization
from src.scraper.core.tasks.extraction import extract_json
from src.scraper.core.tasks.normalization import normalize_json
from src.scraper.core.tasks.screenshot import screenshot
from src.scraper.core.tasks.validation import validate_json


def pipeline():
    return Pipeline.from_caller(
        tasks=[
            screenshot(url, scope_selectors),
            extract_json(prompt),
            validate_json(schema),
            normalize_json(normalize),
        ],
    )


url = lambda ticker: f"https://www.tipranks.com/stocks/{ticker}/forecast"
scope_selectors = ["Month Forecast", "Analyst Ratings"]

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
