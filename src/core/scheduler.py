import random
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


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
            selected_input = random.choice(list(input_options))
            task.execute(selected_input)
        else:
            task.execute()  # global task takes no input
        return True
    else:
        return False
