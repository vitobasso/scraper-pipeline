import glob, re, random
import src.stocks.ticker_screenshot as ticker_screenshot
import src.stocks.flow_yahoo as flow_yahoo
import src.stocks.image_scrape as image_scrape
from src.core.screenshot_validator import validate
from typing import Literal

tickers_path = 'input/ticker-list/acoes-br.csv'
awaiting_screenshot_validation_path = 'output/screenshots/awaiting-validation'
awaiting_extraction_path = 'output/screenshots/awaiting-extraction'
awaiting_data_validation_path = 'output/data/awaiting-validation'
completed_path = 'output/data/awaiting-validation'

flows = {
    'tradingview': {
        'screenshot': ticker_screenshot.screenshot_tradingview,
        'extract': image_scrape.extract_analysis,
        'validate-data': lambda: None,
    },
    'yahoo': {
        'screenshot': flow_yahoo.screenshot_yahoo,
        'extract': flow_yahoo.extract_data,
        'validate-data': flow_yahoo.validate_data,
    },
}
FlowType = Literal[tuple(flows.keys())]


def schedule_next(flow: FlowType):
    _try_phase(flow, 'validate-data', lambda: _get_all_files(awaiting_data_validation_path, flow), flows[flow]['validate-data']) or \
    _try_phase(flow, 'extract', lambda: _get_all_files(awaiting_extraction_path, flow), flows[flow]['extract']) or \
    _try_phase(flow, 'validate-screenshot', lambda: _get_all_files(awaiting_screenshot_validation_path, flow), validate) or \
    _try_phase(flow, 'screenshot', lambda: _find_tickers_awaiting_screenshot(flow), flows[flow]['screenshot'])


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
        - set(_get_all_tickers(awaiting_data_validation_path, filter_term)) \
        - set(_get_all_tickers(awaiting_extraction_path, filter_term)) \
        - set(_get_all_tickers(awaiting_screenshot_validation_path, filter_term))
    )


def _get_ticker(path: str):
    return re.match(r'.*/\w+?-(\w+)+.*', path).group(1)


def _get_all_tickers(dir_path: str, filter_term: str):
    return [_get_ticker(path) for path in glob.glob(f"{dir_path}/*") if filter_term in path]


def _get_all_files(dir_path: str, filter_term: str):
    return [path for path in glob.glob(f"{dir_path}/*") if filter_term in path]
