import json
from collections.abc import Callable

from src.common.util.date_util import timestamp
from src.scraper.core import paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline, TaskFactory
from src.scraper.core.tasks.base import source_task
from src.scraper.services.proxies import random_proxy


def call_api(call: Callable[[str, str], dict]) -> TaskFactory:
    """call: takes a ticker and a proxy and calls an api, returning a dict."""
    execute = lambda pipe, ticker: _call_api(pipe, ticker, call)
    return source_task(execute)


def _call_api(pipe: Pipeline, ticker: str, call: Callable[[str, str], dict]):
    proxy = random_proxy(pipe)
    path = paths.for_pipe(pipe, ticker).stage_dir("validation") / f"{timestamp()}.json"
    print(f"calling api, path: {path}, proxy: {proxy}")
    try:
        data = call(ticker, proxy)
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        log(str(e), ticker, pipe)
