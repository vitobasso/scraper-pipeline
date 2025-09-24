"""
A wrapper for paths.py that adds convenience methods for Pipeline.
Separate from paths.py to avoid circular dependency.
"""

from collections.abc import Iterator
from pathlib import Path

from src.scraper.core.paths import _FAILED, PipelinePaths, for_parts
from src.scraper.core.scheduler import Pipeline


def for_pipe(pipe: Pipeline, ticker: str) -> PipelinePaths:
    """Get path helper for a pipeline and ticker."""
    return for_parts(pipe.asset_class, ticker, pipe.name)


def latest_file(pipe: Pipeline, ticker: str, stage: str) -> Path | None:
    """Get the most recent file in a stage directory, if any."""
    stage_path = for_pipe(pipe, ticker).stage_dir(stage)
    files = [f for f in stage_path.glob("*") if f.is_file()]
    return max(files, key=lambda f: f.stem) if files else None


def waiting_files(pipe: Pipeline, ticker: str, stage: str) -> Iterator[Path]:
    """Get all files in the waiting directory for a stage."""
    stage_path = for_pipe(pipe, ticker).stage_dir(stage)
    return stage_path.glob("*") if stage_path.exists() else []


def failed_files(pipe: Pipeline, ticker: str) -> list[Path]:
    """Get all files in the failed directory."""
    failed_path = for_pipe(pipe, ticker).debug_dir / _FAILED
    return [f for f in failed_path.rglob("*") if f.is_file()] if failed_path.exists() else []
