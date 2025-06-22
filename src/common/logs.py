import logging

from src.common.util import mkdir, timestamp
from src.config import output_root

cache = dict()


def log(msg: str, pipeline: str, ticker: str = '_'):
    logger = _get_logger(pipeline, ticker)
    logger.error(f'{timestamp()}: {msg}')


def _get_logger(pipeline: str, ticker: str):
    name = f'{pipeline}-{ticker}'
    if name in cache:
        return cache[name]
    cache[name] = _create_logger(pipeline, ticker)
    return cache[name]


def _create_logger(pipeline: str, ticker: str):
    name = f'{pipeline}-{ticker}'
    path = _path(pipeline, ticker)
    handler = logging.FileHandler(path)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    return logger


def _path(pipeline: str, ticker: str):
    dir = mkdir(f'{output_root}/{pipeline}/logs')
    return f'{dir}/{ticker}.log'
