import random
from typing import Callable, TypedDict, List
from src.core.util import get_ticker, all_files, mkdir
from src.config import output_dir

tickers_path = 'input/ticker-list/acoes-br.csv'
completed_dir = mkdir(f'{output_dir}/data/awaiting-validation')


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


def seed_task(execute, task_name, pipeline_name):
    return {
        'name': task_name,
        'find_input': lambda: True,
        'execute': execute
    }


def ticker_task(execute, output_dirs, task_name, pipeline_name):
    mid_files = [file
                 for task_output_dir in output_dirs
                 for file in all_files(task_output_dir, pipeline_name)]
    processed_files = mid_files + all_files(completed_dir, pipeline_name)
    return {
        'name': task_name,
        'find_input': lambda: list(set(_load_tickers()) - set([get_ticker(path) for path in processed_files])),
        'execute': execute
    }


def file_task(execute, input_dir, task_name, pipeline_name):
    return {
        'name': task_name,
        'find_input': lambda: all_files(input_dir, pipeline_name),
        'execute': execute
    }


def _load_tickers():
    with open(tickers_path, 'r') as file:
        return [line.strip().lower() for line in file.readlines()]
