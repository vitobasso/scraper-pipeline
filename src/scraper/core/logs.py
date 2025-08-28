import logging
from datetime import datetime

from src.common import util
from src.scraper.core import paths

cache = dict()


def log(msg: str, ticker: str, pipeline: str):
    logger = _get_logger(ticker, pipeline)
    safe_msg = msg.strip().replace("\n", "\\n")
    logger.error(f"{util.timestamp()}: {safe_msg}")


def timestamp_from_log(log_line: str):
    ts_str, _ = log_line.split(": ", 1)
    return datetime.strptime(ts_str, util.timestamp_format)


def _get_logger(ticker: str, pipeline: str):
    name = f"{ticker}-{pipeline}"
    if name in cache:
        return cache[name]
    cache[name] = _create_logger(ticker, pipeline)
    return cache[name]


def _create_logger(ticker: str, pipeline: str):
    name = f"{ticker}-{pipeline}"
    path = paths.errors_log(pipeline, ticker)
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(path)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    return logger
