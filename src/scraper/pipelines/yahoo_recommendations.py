import json

import yfinance

from src.common.util import timestamp
from src.scraper.core import paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import normalize_json, source_task, validate_json
from src.scraper.services.proxies import random_proxy

name = "yahoo_recommendations"


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            source_task(name, call_api),
            validate_json(name, schema),
            normalize_json(name, normalize),
        ],
    )


def call_api(ticker):
    proxy = random_proxy(name)
    path = paths.stage_dir_for(ticker, name, "validation") / f"{timestamp()}.json"
    print(f"scraping, path: {path}, proxy: {proxy}")
    try:
        ticker_obj = yfinance.Ticker(f"{ticker}.SA")
        data = ticker_obj.get_recommendations(proxy=proxy).to_dict()
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        log(str(e), ticker, name)


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
