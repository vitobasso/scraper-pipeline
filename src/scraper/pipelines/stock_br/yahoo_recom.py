import json

import yfinance
from curl_cffi import requests

from src.common import config
from src.common.util.date_util import timestamp
from src.scraper.core import paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import normalize_json, source_task, validate_json
from src.scraper.services.proxies import random_proxy


def pipeline():
    return Pipeline.from_caller(
        tasks=[
            source_task(call_api),
            validate_json(schema),
            normalize_json(normalize),
        ],
    )


def call_api(pipe: Pipeline, ticker: str):
    proxy = random_proxy(pipe)
    path = paths.for_pipe(pipe, ticker).stage_dir("validation") / f"{timestamp()}.json"
    print(f"scraping, path: {path}, proxy: {proxy}")
    try:
        session = requests.Session(impersonate="chrome", verify=config.enforce_https)
        data = yfinance.Ticker(f"{ticker}.SA", session=session).get_recommendations(proxy=proxy).to_dict()
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        log(str(e), ticker, pipe)


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
