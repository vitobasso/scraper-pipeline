import json

import yfinance

from src.core import paths
from src.core.logs import log
from src.core.scheduler import Pipeline
from src.core.tasks import normalize_json, source_task, validate_json
from src.core.util import timestamp
from src.services.proxies import random_proxy

name = "yahoo_chart"


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            source_task(name, call_api),
            validate_json(name, validator, "normalization"),
            normalize_json(name, normalize),
        ],
    )


def call_api(ticker):
    proxy = random_proxy(name)
    path = paths.stage_dir_for(ticker, name, "validation") / f"{timestamp()}.json"
    print(f"scraping, path: {path}, proxy: {proxy}")
    try:
        result = yfinance.Ticker(f"{ticker}.SA").history(period="5y", interval="1d", proxy=proxy, raise_errors=True)
        data = result["Close"].tolist()
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        log(str(e), ticker, name)


validator = lambda data: ["array is empty"] if not data else []

normalize = lambda raw: {
    "1mo": raw[-21:],
    "1y": [v for i, v in enumerate(raw[-252:]) if i % 5 == 0],
    "5y": [v for i, v in enumerate(raw) if i % 20 == 0],
}
