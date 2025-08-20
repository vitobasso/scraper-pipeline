import json

import yfinance

from src.core import paths
from src.core.logs import log
from src.core.scheduler import Pipeline
from src.core.tasks import validate_json, source_task
from src.core.util import timestamp
from src.services.proxies import random_proxy

name = 'yahoo_chart'


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            source_task(name, call_api),
            validate_json(name, validator),
        ],
    )


def call_api(ticker):
    proxy = random_proxy()
    path = paths.stage_dir_for(ticker, name, "validation") / f'{timestamp()}.json'
    print(f'scraping, path: {path}, proxy: {proxy}')
    try:
        result = yfinance.Ticker(f'{ticker}.SA').history(period="5y", interval="1d", proxy=proxy, raise_errors=True)
        data = result["Close"].tolist()
        with open(path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        log(str(e), ticker, name)


validator = lambda data: ["array is empty"] if not data else []
