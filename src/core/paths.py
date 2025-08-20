from pathlib import Path
from typing import List

from src.config import output_root
from src.core.util import mkdir

"""
Path structure per ticker and pipeline:

{ticker}/
    {pipeline}/
        waiting/
            extraction/
            validation/
            normalization/
        ready/
        debug/
            failed/
                extraction/
                validation/
                normalization/
            processed/
            errors.log
        
- waiting: input for intermediate pipeline stages
- ready: final output, ready to be consumed via api
- debug: can be discarded or optionally kept for debug purposes
- errors.log determines whether we should stop insisting on a ticker pipeline
"""


def pipeline_dir(ticker: str, pipeline: str):
    return Path(output_root) / ticker / pipeline


def pipeline_dir_for(child_path: Path) -> Path:
    ticker, pipeline = extract_ticker_pipeline(child_path)
    return pipeline_dir(ticker, pipeline)


def stage_dir(pipe_dir: Path, stage: str):
    if stage == "ready":
        return mkdir(pipe_dir / "ready")
    else:
        return mkdir(pipe_dir / "waiting" / stage)


def stage_dir_for(ticker: str, pipeline: str, stage: str):
    return stage_dir(pipeline_dir(ticker, pipeline), stage)


def failed_dir(pipe_dir: Path, stage: str):
    return mkdir(pipe_dir / "debug" / "failed" / stage)


def processed_dir(pipe_dir: Path):
    return mkdir(pipe_dir / "debug" / "processed")


def latest_file(ticker: str, pipeline: str, stage: str) -> Path | None:
    stage = stage_dir(pipeline_dir(ticker, pipeline), stage)
    files = [f for f in stage.glob("*") if f.is_file()]
    if not files:
        return None
    return max(files, key=lambda f: f.stem)


def waiting_files(ticker: str, pipeline: str, stage: str) -> List[Path]:
    stage = pipeline_dir(ticker, pipeline) / "waiting" / stage
    return stage.glob("*") if stage.exists() else []


def has_waiting_files(ticker: str, pipeline: str) -> bool:
    waiting = pipeline_dir(ticker, pipeline) / "waiting"
    return any(f.is_file() for f in waiting.glob("**/*"))


def failed_files(ticker: str, pipeline: str) -> List[Path]:
    failed = pipeline_dir(ticker, pipeline) / "failed"
    return failed.glob("*") if failed.exists() else []


def errors_log(pipeline, ticker):
    debug = mkdir(pipeline_dir(ticker, pipeline) / "debug")
    return debug / "errors.log"


def extract_ticker_pipeline(child_path: Path) -> tuple[str, str]:
    for marker in ("waiting", "ready", "debug"):
        if marker in child_path.parts:
            idx = child_path.parts.index(marker)
            return child_path.parts[idx - 2], child_path.parts[idx - 1]
    raise ValueError(f"Not a pipeline path: {child_path}")
