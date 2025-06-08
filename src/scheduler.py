import random
from typing import Callable, TypedDict, List
from src.core.util import filename_before_timestamp, all_files


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


def seed_task(execute, output_dir):
    return {
        'find_input': lambda: False if all_files(output_dir) else True,
        'execute': execute
    }


def line_task(execute, input_path, output_dir):
    all_lines = _load_lines(input_path)
    progressed_lines = [filename_before_timestamp(path) for path in all_files(output_dir)]
    return {
        'find_input': lambda: list(set(all_lines) - set(progressed_lines)),
        'execute': execute
    }


def file_task(execute, input_dir):
    return {
        'find_input': lambda: all_files(input_dir),
        'execute': execute
    }


def _load_lines(path):
    with open(path, 'r') as file:
        return [line.strip().lower() for line in file.readlines()]
