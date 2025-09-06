import yfinance
from curl_cffi import requests

from src.common import config
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import normalization
from src.scraper.core.tasks.api_call import call_api
from src.scraper.core.tasks.normalization import normalize_json
from src.scraper.core.tasks.validation import validate_json


def pipeline():
    return Pipeline.from_caller(
        tasks=[
            call_api(call),
            validate_json(schema),
            normalize_json(normalize),
        ],
    )


def call(ticker: str, proxy: str):
    session = requests.Session(impersonate="chrome", verify=config.enforce_https)
    return yfinance.Ticker(f"{ticker}.SA", session=session).get_analyst_price_targets(proxy=proxy)


schema = {
    "high": float,
    "mean": float,
    "low": float,
}

normalize = normalization.rename_keys(
    {
        "high": "max",
        "mean": "avg",
        "low": "min",
    }
)
