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


url = lambda ticker: f"https://tradingview.com/symbols/{ticker}/forecast"
scope_selectors = ["Price target", "Analyst rating"]

prompt = """
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
    "analyst_rating": {
        "strong_buy": int,
        "buy": int,
        "hold": int,
        "sell": int,
        "strong_sell": int,
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
