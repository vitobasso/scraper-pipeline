from pathlib import Path

from src.common.services import repository
from src.scraper.core import progress
from src.scraper.core.scheduler import Executable, Task, TaskFactory


def source_task(execute: Executable[str]) -> TaskFactory:
    get_progress = lambda pipe: progress.progress(pipe, set(repository.query_tickers(pipe.asset_class)))
    return lambda pipe: Task(
        find_input=lambda: get_progress(pipe).available(),
        progress=lambda: get_progress(pipe),
        execute=lambda arg: execute(pipe, arg),
        pipeline=pipe,
    )


def global_task(execute) -> TaskFactory:
    # a source task that takes no input
    # find_input returns a bool indicating whether the task is not done yet
    return lambda pipe: Task(
        find_input=lambda: not progress.has_recent_files(pipe, "_global", "ready"),
        progress=lambda: progress.progress(pipe, {"_global"}),
        execute=lambda: execute(pipe),
        pipeline=pipe,
    )


def intermediate_task(execute: Executable[Path], stage: str) -> TaskFactory:
    return lambda pipe: Task(
        find_input=lambda: progress.intermediate_input(pipe, stage),
        progress=None,  # pipeline progress is based on the source task
        execute=lambda arg: execute(pipe, arg),
        pipeline=pipe,
    )
