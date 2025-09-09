import inspect
import random
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeVar, get_args

from src.common.services.repository import query_tickers


@dataclass
class Progress:
    scope: set[str]
    ready: set[str]
    waiting: set[str]
    aborted: set[str]

    def available(self) -> set[str]:
        return self.pending() - self.waiting

    def pending(self) -> set[str]:
        return self.scope - self.ready - self.aborted

    def is_done(self) -> bool:
        return len(self.pending()) <= 0


@dataclass
class Task:
    find_input: Callable[[], set[str | Path] | bool]
    progress: Callable[[], Progress] | None
    execute: Callable
    pipeline: "Pipeline"
    requires: list[str]


AssetClass = Literal["stock_br", "reit_br"]


@dataclass
class Pipeline:
    name: str
    asset_class: AssetClass
    tasks: list[Task]

    @classmethod
    def from_caller(cls, tasks: list["TaskFactory"], stack_frame_index: int = 1) -> "Pipeline":
        """
        Construct a Pipeline instance based on the caller’s module filename.

        :param tasks: A list of TaskFactory callables to create tasks for the pipeline.
        :param stack_frame_index: Index of the call stack frame to use for extracting the module filename.
                                  Default is 1 (direct caller). Increase by 1 for each additional layer of indirection.
        """
        asset_class, name = _get_pipeline_name(inspect.stack()[stack_frame_index].filename)
        pipeline = cls(name=name, asset_class=asset_class, tasks=[])
        pipeline.tasks = [t(pipeline) for t in tasks]
        return pipeline

    def run_task(self):
        for task in self.tasks[::-1]:
            if _try_task(task):
                return

    def progress(self) -> Progress:
        return self.tasks[0].progress()

    def is_done(self):
        return self.progress().is_done()

    def dependencies(self):
        return {r for t in self.tasks for r in t.requires}


TaskFactory = Callable[[Pipeline], Task]
A = TypeVar("A")
Executable = Callable[[Pipeline, A], any]


@dataclass
class Manager:
    pipes: dict[str, Pipeline]

    @classmethod
    def from_pipelines(cls, pipelines: list[Pipeline]) -> "Manager":
        return cls({pipe.name: pipe for pipe in pipelines})

    def is_available(self, pipe: Pipeline):
        return not pipe.is_done() and all(self.pipes[r].is_done() for r in pipe.dependencies())

    def run_next(self):
        pending = [p for p in self.pipes.values() if self.is_available(p)]
        if pending:
            p = random.choice(pending)
            p.run_task()
            return True
        else:
            return False


def _try_task(task: Task):
    input_options = task.find_input()
    if input_options:
        if isinstance(input_options, set):
            selected_input = _select_input(input_options, task.pipeline.asset_class)
            task.execute(selected_input)
        else:
            task.execute()  # global task takes no input
        return True
    else:
        return False


def _select_input(options: set[A], asset_class: AssetClass) -> A:
    priority = query_tickers(asset_class)
    pmap = {ticker: i for i, ticker in enumerate(priority)}

    def _extract_ticker(opt: A):
        text = opt if isinstance(opt, str) else str(opt)
        for ticker in priority:
            if ticker in text:
                return ticker
        return None

    return min(options, key=lambda opt: pmap.get(_extract_ticker(opt), float("inf")))


def _get_pipeline_name(caller_file) -> tuple[AssetClass, str]:
    p = Path(caller_file)
    asset_class = p.parent.name
    if asset_class not in list(get_args(AssetClass)):
        raise ValueError(f"Unknown asset class: {asset_class}")
    return asset_class, p.stem  # type: ignore
