from collections.abc import Callable
from pathlib import Path

from src.common.services import repository
from src.scraper.core import extraction, normalization, progress, validation
from src.scraper.core.scheduler import Task


def source_task(pipeline: str, execute: Callable[[str], any]) -> Task:
    return Task(
        find_input=lambda: progress.progress(pipeline, set(repository.query_tickers())).available(),
        progress=lambda: progress.progress(pipeline, set(repository.query_tickers())),
        execute=execute,
    )


def intermediate_task(execute: Callable[[Path], any], pipeline: str, stage: str) -> Task:
    return Task(
        find_input=lambda: progress.intermediate_input(pipeline, stage),
        progress=None,  # pipeline progress is based on the source task
        execute=execute,
    )


def global_task(pipeline: str, execute) -> Task:
    # a source task that takes no input
    # find_input is a bool indicating whether the task is not done yet
    return Task(
        find_input=lambda: not progress.has_recent_files("_global", pipeline, "ready"),
        progress=lambda: progress.progress(pipeline, {"_global"}),
        execute=execute,
    )


def extract_json(pipeline: str, prompt: str, next_stage: str = "validation") -> Task:
    execute = lambda path: extraction.extract_json(path, prompt, next_stage)
    return intermediate_task(execute, pipeline, "extraction")


def validate_json(pipeline: str, arg, next_stage: str = "normalization") -> Task:
    if isinstance(arg, dict):
        return _validate_json_schema(pipeline, arg, next_stage)
    elif callable(arg):
        return _validate_json_callable(pipeline, arg, next_stage)
    else:
        raise TypeError(f"validate_data not implemented for type: {type(arg)}")


def _validate_json_schema(pipeline: str, schema, next_stage: str) -> Task:
    execute = lambda path: validation.validate_schema(path, schema, next_stage)
    return intermediate_task(execute, pipeline, "validation")


def _validate_json_callable(pipeline: str, validator: Callable[[str], list], next_stage: str) -> Task:
    execute = lambda path: validation.validate_json(path, validator, next_stage)
    return intermediate_task(execute, pipeline, "validation")


def normalize_json(pipeline: str, function: Callable, next_stage: str = "ready") -> Task:
    execute = lambda path: normalization.normalize_json(path, function, next_stage)
    return intermediate_task(execute, pipeline, "normalization")
