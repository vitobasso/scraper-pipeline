import yfinance
from curl_cffi import requests

from src.common import config
from src.scraper.core.scheduler import Pipeline
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
    return yfinance.Ticker(f"{ticker}.SA", session=session).get_recommendations(proxy=proxy).to_dict()


schema = {
    "period": {
        "0": str,
    },
    "strongBuy": {
        "0": int,
    },
    "buy": {
        "0": int,
    },
    "hold": {
        "0": int,
    },
    "sell": {
        "0": int,
    },
    "strongSell": {
        "0": int,
    },
}

normalize = lambda raw: {
    "strong_buy": raw.get("strongBuy", {}).get("0"),
    "buy": raw.get("buy", {}).get("0"),
    "hold": raw.get("hold", {}).get("0"),
    "sell": raw.get("sell", {}).get("0"),
    "strong_sell": raw.get("strongSell", {}).get("0"),
}
