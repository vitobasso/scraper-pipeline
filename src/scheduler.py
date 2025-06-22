import random
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

from src.common.util import filename_before_timestamp, all_files, file_lines
from src.config import error_limit


@dataclass
class Task:
    is_finished: Callable[[], bool]
    find_input: Callable[[], any]
    execute: Callable


@dataclass
class Progress:
    max: int
    current: int


@dataclass
class Pipeline:
    name: str
    tasks: List[Task]
    progress: Progress

    def schedule_next(self):
        for task in self.tasks[::-1]:
            if _try_task(task):
                return

    def report(self):
        max = self.progress.max
        current = self.progress.current
        print(f'{self.name:<20} {f"{current}/{max}":>7}')


def _try_task(task):
    input_options = task.find_input()
    if input_options and not task.is_finished():
        if isinstance(input_options, list):
            selected_input = random.choice(input_options)
            task.execute(selected_input)
        else:
            task.execute()
        return True
    else:
        return False


def seed_task(execute, output_dir) -> Task:
    return Task(
        find_input=lambda: True,
        execute=execute,
        is_finished=lambda: all_files(output_dir),
    )


def line_task(execute, input_path, output_dir) -> Task:
    return Task(
        find_input=lambda: _find_input(input_path, output_dir),
        execute=execute,
        is_finished=lambda: False,
    )


def file_task(execute, input_dir) -> Task:
    return Task(
        find_input=lambda: all_files(input_dir),
        execute=execute,
        is_finished=lambda: False,
    )


def aggregate_task(execute, input_path, output_dir, aggregate_dir) -> Task:
    return Task(
        find_input=lambda: not _find_input(input_path, output_dir),
        execute=execute,
        is_finished=lambda: all_files(aggregate_dir),
    )


def _find_input(input_path, output_dir):
    all_lines = [line.lower() for line in file_lines(input_path)]
    progressed_lines = [filename_before_timestamp(path)
                        for path in all_files(output_dir) if 'awaiting' in path or 'ready' in path]
    aborted_lines = [Path(path).stem
                     for path in all_files(f'{output_dir}/logs') if len(file_lines(path)) > error_limit]
    return list(set(all_lines) - set(progressed_lines) - set(aborted_lines))


def seed_progress(completed_dir) -> Progress:
    return Progress(
        max=1,
        current=1 if len(all_files(completed_dir)) else 0
    )


def line_progress(input_path, completed_dir) -> Progress:
    return Progress(
        max=len(file_lines(input_path)),
        current=len(all_files(completed_dir)),
    )
