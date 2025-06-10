import random
from typing import Callable, TypedDict, List
from src.common.util import filename_before_timestamp, all_files, file_lines


class Task(TypedDict):
    name: str
    is_ready: bool
    is_finished: bool
    find_input: Callable
    execute: Callable


class Progress(TypedDict):
    max: int
    current: int


class Pipeline(TypedDict):
    name: str
    tasks: List[Task]
    progress: Progress


def schedule_next(pipeline: Pipeline):
    for task in pipeline['tasks'][::-1]:
        if _try_task(task):
            return


def _try_task(task):
    input_options = task['find_input']()
    if input_options and not task['is_finished']():
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
        'find_input': lambda: True,
        'execute': execute,
        'is_finished': lambda: all_files(output_dir),
    }


def line_task(execute, input_path, output_dir):
    return {
        'find_input': lambda: _find_input(input_path, output_dir),
        'execute': execute,
        'is_finished': lambda: False,
    }


def file_task(execute, input_dir):
    return {
        'find_input': lambda: all_files(input_dir),
        'execute': execute,
        'is_finished': lambda: False,
    }


def aggregate_task(execute, input_path, output_dir, aggregate_dir):
    return {
        'find_input': lambda: not _find_input(input_path, output_dir),
        'execute': execute,
        'is_finished': lambda: all_files(aggregate_dir),
    }


def _find_input(input_path, output_dir):
    all_lines = [line.lower() for line in file_lines(input_path)]
    progressed_lines = [filename_before_timestamp(path)
                        for path in all_files(output_dir) if 'awaiting' in path or 'ready' in path]
    return list(set(all_lines) - set(progressed_lines))


def line_progress(input_path, completed_dir) -> Progress:
    return {
        'max': len(file_lines(input_path)),
        'current': len(all_files(completed_dir)),
    }


def report(pipeline: Pipeline):
    max = pipeline['progress']['max']
    current = pipeline['progress']['current']
    print(f'{pipeline["name"]:<20} {f"{current}/{max}":>7}')
