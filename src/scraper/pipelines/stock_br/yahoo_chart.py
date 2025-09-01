import json

import yfinance

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
            validate_json(validator, "normalization"),
            normalize_json(normalize),
        ],
    )


def call_api(pipe: Pipeline, ticker: str):
    proxy = random_proxy(pipe)
    path = paths.stage_dir_for(pipe, ticker, "validation") / f"{timestamp()}.json"
    print(f"scraping, path: {path}, proxy: {proxy}")
    try:
        result = yfinance.Ticker(f"{ticker}.SA").history(period="5y", interval="1d", proxy=proxy, raise_errors=True)
        data = result["Close"].tolist()
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        log(str(e), ticker, pipe)


validator = lambda data: ["array is empty"] if not data else []

normalize = lambda raw: {
    "1mo": raw[-21:],
    "1y": [v for i, v in enumerate(raw[-252:]) if i % 5 == 0],
    "5y": [v for i, v in enumerate(raw) if i % 20 == 0],
}
