import glob, re, random
from src.flows import generic_screenshot, generic_extract, yahoo, investidor10
from src.core import screenshot_validator
from typing import Literal

tickers_path = 'input/ticker-list/acoes-br.csv'
awaiting_screenshot_validation_path = 'output/screenshots/awaiting-validation'
awaiting_extraction_path = 'output/screenshots/awaiting-extraction'
awaiting_data_validation_path = 'output/data/awaiting-validation'
completed_path = 'output/data/awaiting-validation'

flows = {
    'tradingview': {
        'screenshot': generic_screenshot.screenshot_tradingview,
        'extract_data': generic_extract.extract_analysis,
        'validate_data': lambda: None,
    },
    'yahoo': {
        'screenshot': yahoo.screenshot,
        'extract_data': yahoo.extract_data,
        'validate_data': yahoo.validate_data,
    },
    'investidor10': {
        'screenshot': investidor10.screenshot,
        'extract_data': investidor10.extract_data,
        'validate_data': lambda: None,
    },
}
FlowType = Literal[tuple(flows.keys())]
Phase = Literal['screenshot', 'validate_screenshot', 'extract_data', 'validate_data']


def schedule_next(flow: FlowType):
    _try_phase(flow, 'validate_data', lambda: _get_all_files(awaiting_data_validation_path, flow), flows[flow]['validate_data']) or \
    _try_phase(flow, 'extract_data', lambda: _get_all_files(awaiting_extraction_path, flow), flows[flow]['extract_data']) or \
    _try_phase(flow, 'validate_screenshot', lambda: _get_all_files(awaiting_screenshot_validation_path, flow), screenshot_validator.validate) or \
    _try_phase(flow, 'screenshot', lambda: _find_tickers_awaiting_screenshot(flow), flows[flow]['screenshot'])


def _try_phase(flow: FlowType, phase: Phase, find_input, execute):
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
