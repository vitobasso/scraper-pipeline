import json

import yfinance
from curl_cffi import requests

from src.common import config
from src.common.util.date_util import timestamp
from src.scraper.core import normalization, paths
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
        data = yfinance.Ticker(f"{ticker}.SA", session=session).get_analyst_price_targets(proxy=proxy)
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        log(str(e), ticker, pipe)


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
