import random
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

from src.services.repository import query_tickers


@dataclass
class Progress:
    full_domain: set[str]
    ready: set[str]
    waiting: set[str]
    aborted: set[str]

    def available(self) -> set[str]:
        return self.full_domain - self.waiting - self.ready - self.aborted

    def pending(self) -> set[str]:
        return self.full_domain - self.ready - self.aborted

    def is_done(self) -> bool:
        return len(self.pending()) <= 0


@dataclass
class Task:
    find_input: Callable[[], set[str | Path] | bool]
    progress: Callable[[], Progress] | None
    execute: Callable


@dataclass
class Pipeline:
    name: str
    tasks: list[Task]

    def run_next(self):
        for task in self.tasks[::-1]:
            if _try_task(task):
                return

    def progress(self) -> Progress:
        return self.tasks[0].progress()

    def is_done(self):
        return self.progress().is_done()


def _try_task(task):
    input_options = task.find_input()
    if input_options:
        if isinstance(input_options, set):
            selected_input = _select_input(input_options)
            task.execute(selected_input)
        else:
            task.execute()  # global task takes no input
        return True
    else:
        return False


A = TypeVar("A", str, Path)


def _select_input(options: set[A]) -> A:
    priority = query_tickers()
    pmap = {ticker: i for i, ticker in enumerate(priority)}

    def _extract_ticker(opt: A):
        text = opt if isinstance(opt, str) else str(opt)
        for ticker in priority:
            if ticker in text:
                return ticker
        return None

    return min(options, key=lambda opt: pmap.get(_extract_ticker(opt), float("inf")))
