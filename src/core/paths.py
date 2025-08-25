from pathlib import Path

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


def split_files(input_path: Path, current_stage: str, next_stage: str, out_ext: str | None = None) -> list[Path]:
    pipe_dir = pipeline_dir_for(input_path)
    output_file = f"{input_path.stem}.{out_ext}" if out_ext else input_path.name
    output = stage_dir(pipe_dir, next_stage) / output_file
    failed = failed_dir(pipe_dir, current_stage) / input_path.name
    processed = processed_dir(pipe_dir) / input_path.name
    return [output, failed, processed]


def latest_file(ticker: str, pipeline: str, stage: str) -> Path | None:
    stage = stage_dir(pipeline_dir(ticker, pipeline), stage)
    files = [f for f in stage.glob("*") if f.is_file()]
    if not files:
        return None
    return max(files, key=lambda f: f.stem)


def waiting_files(ticker: str, pipeline: str, stage: str) -> list[Path]:
    stage = pipeline_dir(ticker, pipeline) / "waiting" / stage
    return stage.glob("*") if stage.exists() else []


def has_waiting_files(ticker: str, pipeline: str) -> bool:
    waiting = pipeline_dir(ticker, pipeline) / "waiting"
    return any(f.is_file() for f in waiting.rglob("*"))


def failed_files(ticker: str, pipeline: str) -> list[Path]:
    failed = pipeline_dir(ticker, pipeline) / "debug" / "failed"
    return [f for f in failed.rglob("*") if f.is_file()] if failed.exists() else []


def errors_log(pipeline, ticker):
    debug = mkdir(pipeline_dir(ticker, pipeline) / "debug")
    return debug / "errors.log"


def extract_ticker_pipeline(child_path: Path) -> tuple[str, str]:
    for marker in ("waiting", "ready", "debug"):
        if marker in child_path.parts:
            idx = child_path.parts.index(marker)
            return child_path.parts[idx - 2], child_path.parts[idx - 1]
    raise ValueError(f"Not a pipeline path: {child_path}")
