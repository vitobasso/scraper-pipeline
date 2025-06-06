import random
from typing import Callable, TypedDict
from src.core.util import get_ticker, all_files, mkdir
from src.config import output_dir

tickers_path = 'input/ticker-list/acoes-br.csv'
awaiting_screenshot_validation_path = mkdir(f'{output_dir}/screenshots/awaiting-validation')
awaiting_extraction_path = mkdir(f'{output_dir}/screenshots/awaiting-extraction')
awaiting_data_validation_path = mkdir(f'{output_dir}/data/awaiting-validation')
completed_path = mkdir(f'{output_dir}/data/awaiting-validation')


class Flow(TypedDict):
    name: str
    screenshot: Callable
    validate_screenshot: Callable
    extract_data: Callable
    validate_data: Callable


def schedule_next(flow: Flow):
    flow_name = flow['name']
    _try_phase(flow['validate_data'], lambda: all_files(awaiting_data_validation_path, flow_name)) or \
    _try_phase(flow['extract_data'], lambda: all_files(awaiting_extraction_path, flow_name)) or \
    _try_phase(flow['validate_screenshot'], lambda: all_files(awaiting_screenshot_validation_path, flow_name)) or \
    _try_phase(flow['screenshot'], lambda: _all_tickers_awaiting_screenshot(flow_name))


def _try_phase(execute, find_input):
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


def _all_tickers_awaiting_screenshot(filter_term: str):
    return list(
        set(_load_tickers()) \
        - set(_all_tickers(completed_path, filter_term)) \
        - set(_all_tickers(awaiting_data_validation_path, filter_term)) \
        - set(_all_tickers(awaiting_extraction_path, filter_term)) \
        - set(_all_tickers(awaiting_screenshot_validation_path, filter_term))
    )


def _all_tickers(dir_path: str, filter_term: str):
    return [get_ticker(path) for path in all_files(dir_path, filter_term)]
