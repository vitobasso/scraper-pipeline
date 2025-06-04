import os, glob, re, random
import src.stocks.ticker_screenshot as ticker_screenshot
from src.core.screenshot_validator import validate
from src.stocks.stocks_image_scrape import extract_analysis

tickers_path = 'input/ticker-list/acoes-br.csv'
awaiting_validation_path = 'output/screenshots/awaiting-validation'
awaiting_extraction_path = 'output/screenshots/awaiting-extraction'
completed_path = 'output/data'


def schedule_next(flow: str):
    _try_phase(flow, 'extract', lambda: _get_all_files(awaiting_extraction_path, flow), extract_analysis) or \
    _try_phase(flow, 'validate', lambda: _get_all_files(awaiting_validation_path, flow), validate) or \
    _try_phase(flow, 'screenshot', lambda: _find_tickers_awaiting_screenshot(flow), ticker_screenshot.screenshot_tradingview)


def _try_phase(flow: str, phase: str, find_input, execute):
    input_options = find_input()
    if input_options:
        ticker = random.choice(input_options)
        execute(ticker)
        return True
    else:
        return False


def _load_tickers():
    with open(tickers_path, 'r') as file:
        return [line.strip().lower() for line in file.readlines()]


def _find_tickers_awaiting_screenshot(filter_term: str):
    return list(
        set(_load_tickers()) \
        - set(_get_all_tickers(completed_path, filter_term)) \
        - set(_get_all_tickers(awaiting_extraction_path, filter_term)) \
        - set(_get_all_tickers(awaiting_validation_path, filter_term))
    )


def _get_ticker(path: str):
    return re.match(r'.*/\w+?-(\w+)+.*', path).group(1)


def _get_all_tickers(dir_path: str, filter_term: str):
    return [_get_ticker(path) for path in glob.glob(f"{dir_path}/*") if filter_term in path]


def _get_all_files(dir_path: str, filter_term: str):
    return [path for path in glob.glob(f"{dir_path}/*") if filter_term in path]

