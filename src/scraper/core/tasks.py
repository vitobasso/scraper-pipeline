from collections.abc import Callable
from pathlib import Path

from src.common.services import repository
from src.scraper.core import extraction, normalization, progress, validation
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


def extract_json(prompt: str, next_stage: str = "validation") -> TaskFactory:
    execute = lambda pipe, path: extraction.extract_json(path, prompt, next_stage)
    return intermediate_task(execute, "extraction")


def validate_json(arg, next_stage: str = "normalization") -> TaskFactory:
    if isinstance(arg, dict):
        return _validate_json_schema(arg, next_stage)
    elif callable(arg):
        return _validate_json_callable(arg, next_stage)  # type: ignore
    else:
        raise TypeError(f"validate_data not implemented for type: {type(arg)}")


def _validate_json_schema(schema, next_stage: str) -> TaskFactory:
    execute = lambda pipe, path: validation.validate_schema(path, schema, next_stage)
    return intermediate_task(execute, "validation")


def _validate_json_callable(validator: Callable[[str], list], next_stage: str) -> TaskFactory:
    execute = lambda pipe, path: validation.validate_json(path, validator, next_stage)
    return intermediate_task(execute, "validation")


def normalize_json(function: Callable, next_stage: str = "ready") -> TaskFactory:
    execute = lambda pipe, path: normalization.normalize_json(path, function, next_stage)
    return intermediate_task(execute, "normalization")


def normalize_csv(function: Callable, next_stage: str = "ready") -> TaskFactory:
    execute = lambda pipe, path: normalization.normalize_csv(path, function, next_stage)
    return intermediate_task(execute, "normalization")
