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
    total: int
    done: int
    progress: int
    failed: int


@dataclass
class Pipeline:
    name: str
    tasks: List[Task]
    progress: Progress

    def schedule_next(self):
        for task in self.tasks[::-1]:
            if _try_task(task):
                return


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
    progressed_lines = _progressed(output_dir)
    completed_lines = _completed(output_dir)
    aborted_lines = _aborted(output_dir)
    return list(set(all_lines) - set(progressed_lines) - set(completed_lines) - set(aborted_lines))


def _progressed(output_dir):
    return [filename_before_timestamp(path)
            for path in all_files(output_dir) if 'awaiting' in path]


def _completed(output_dir):
    return [filename_before_timestamp(path)
            for path in all_files(output_dir) if 'ready' in path]


def _aborted(output_dir):
    return [Path(path).stem
            for path in all_files(f'{output_dir}/logs') if len(file_lines(path)) > error_limit]


def seed_progress(output_dir) -> Progress:
    return _progress(None, output_dir)


def line_progress(input_path, output_dir) -> Progress:
    return _progress(input_path, output_dir)


def _progress(input_path, output_dir) -> Progress:
    return Progress(
        total=len(file_lines(input_path)) if input_path else 1,
        done=len(_completed(output_dir)),
        progress=len(_progressed(output_dir)),
        failed=len(_aborted(output_dir)),
    )


def report(pipelines: List[Pipeline]):
    print(f'{"pipeline":<20} {"pending":>7} {"progress":>7} {"done":>7} {"failed":>7}')
    for p in pipelines:
        done = p.progress.done
        progress = p.progress.progress
        failed = p.progress.failed
        pending = p.progress.total - done - progress - failed
        print(f'{p.name:<20} {pending:>7} {progress:>7} {done:>7} {failed:>7}')
