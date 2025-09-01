from src.scraper.core import normalization
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.screenshot import ss_common_ancestor
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
    ss_common_ancestor(
        ticker, pipe, f"https://tradingview.com/symbols/{ticker}/forecast", ["Price target", "Analyst rating"]
    )


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
