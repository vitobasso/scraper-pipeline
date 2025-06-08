import random
from typing import Callable, TypedDict, List
from src.core.util import get_ticker, all_files

tickers_path = 'input/ticker-list/acoes-br.csv'


class Task(TypedDict):
    name: str
    find_input: Callable
    execute: Callable


class Pipeline(TypedDict):
    name: str
    tasks: List[Task]


def schedule_next(pipeline: Pipeline):
    for task in pipeline['tasks'][::-1]:
        if _try_task(task):
            return


def _try_task(task):
    input_options = task['find_input']()
    if input_options:
        if isinstance(input_options, list):
            selected_input = random.choice(input_options)
            task['execute'](selected_input)
        else:
            task['execute']()
        return True
    else:
        return False


def seed_task(execute):
    return {
        'find_input': lambda: True,
        'execute': execute
    }


def ticker_task(execute, output_dir):
    output_tickers = [get_ticker(path) for path in all_files(output_dir)]
    return {
        'find_input': lambda: list(set(_load_tickers()) - set(output_tickers)),
        'execute': execute
    }


def file_task(execute, input_dir):
    return {
        'find_input': lambda: all_files(input_dir),
        'execute': execute
    }


def _load_tickers():
    with open(tickers_path, 'r') as file:
        return [line.strip().lower() for line in file.readlines()]
