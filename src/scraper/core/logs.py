import logging
from datetime import datetime
from pathlib import Path

from src.common.util import date_util
from src.scraper.core import paths
from src.scraper.core.scheduler import Pipeline

cache = dict()


def log(msg: str, ticker: str, pipeline: Pipeline):
    _log(msg, pipeline.asset_class, ticker, pipeline.name)


def log_for_path(msg: str, path: Path):
    asset_class, ticker, pipe_name = paths.extract_ticker_pipeline(path)
    _log(msg, asset_class, ticker, pipe_name)


def _log(msg: str, asset_class: str, ticker: str, pipe_name: str):
    logger = _get_logger(asset_class, ticker, pipe_name)
    safe_msg = msg.strip().replace("\n", "\\n")
    logger.error(f"{date_util.timestamp()}: {safe_msg}")


def timestamp_from_log(log_line: str):
    ts_str, _ = log_line.split(": ", 1)
    return datetime.strptime(ts_str, date_util.timestamp_format)


def _get_logger(asset_class: str, ticker: str, pipe_name: str):
    name = _get_logger_name(asset_class, ticker, pipe_name)
    if name in cache:
        return cache[name]
    cache[name] = _create_logger(asset_class, ticker, pipe_name)
    return cache[name]


def _create_logger(asset_class: str, ticker: str, pipe_name: str):
    name = _get_logger_name(asset_class, ticker, pipe_name)
    path = paths.errors_log_for_parts(asset_class, ticker, pipe_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(path)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    return logger


def _get_logger_name(asset_class: str, ticker: str, pipe_name: str):
    return f"{asset_class}-{ticker}-{pipe_name}"
