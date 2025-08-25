from src.core import normalization
from src.core.scheduler import Pipeline
from src.core.screenshot import ss_common_ancestor
from src.core.tasks import extract_json, normalize_json, source_task, validate_json

name = "tradingview"


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
        ticker, name, f"https://tradingview.com/symbols/{ticker}/forecast", ["Price target", "Analyst rating"]
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
