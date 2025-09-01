from pathlib import Path

from src.common.config import data_root
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.util.files import mkdir

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


def pipeline_dir(pipe: Pipeline, ticker: str):
    return pipeline_dir_for_parts(pipe.asset_class, ticker, pipe.name)


def pipeline_dir_for_parts(asset_class: str, ticker: str, pipeline_name: str):
    return Path(data_root) / asset_class / ticker / pipeline_name


def pipeline_dir_for_child(child_path: Path) -> Path:
    asset_class, ticker, pipeline_name = extract_ticker_pipeline(child_path)
    return pipeline_dir_for_parts(asset_class, ticker, pipeline_name)


def stage_dir(pipe_dir: Path, stage: str):
    if stage == "ready":
        return mkdir(pipe_dir / "ready")
    else:
        return mkdir(pipe_dir / "waiting" / stage)


def stage_dir_for(pipe: Pipeline, ticker: str, stage: str):
    return stage_dir(pipeline_dir(pipe, ticker), stage)


def stage_dir_for_parts(asset_class: str, ticker: str, pipeline_name: str, stage: str):
    return stage_dir(pipeline_dir_for_parts(asset_class, ticker, pipeline_name), stage)


def _failed_dir(pipe_dir: Path, stage: str):
    return mkdir(pipe_dir / "debug" / "failed" / stage)


def _processed_dir(pipe_dir: Path):
    return mkdir(pipe_dir / "debug" / "processed")


def split_files(input_path: Path, current_stage: str, next_stage: str, out_ext: str | None = None) -> list[Path]:
    pipe_dir = pipeline_dir_for_child(input_path)
    output_file = f"{input_path.stem}.{out_ext}" if out_ext else input_path.name
    output = stage_dir(pipe_dir, next_stage) / output_file
    failed = _failed_dir(pipe_dir, current_stage) / input_path.name
    processed = _processed_dir(pipe_dir) / input_path.name
    return [output, failed, processed]


def latest_file(pipe: Pipeline, ticker: str, stage: str) -> Path | None:
    stage = stage_dir(pipeline_dir(pipe, ticker), stage)
    files = [f for f in stage.glob("*") if f.is_file()]
    if not files:
        return None
    return max(files, key=lambda f: f.stem)


def waiting_files(pipe: Pipeline, ticker: str, stage: str) -> list[Path]:
    stage = pipeline_dir(pipe, ticker) / "waiting" / stage
    return stage.glob("*") if stage.exists() else []


def has_waiting_files(pipe: Pipeline, ticker: str) -> bool:
    waiting = pipeline_dir(pipe, ticker) / "waiting"
    return any(f.is_file() for f in waiting.rglob("*"))


def failed_files(pipe: Pipeline, ticker: str) -> list[Path]:
    failed = pipeline_dir(pipe, ticker) / "debug" / "failed"
    return [f for f in failed.rglob("*") if f.is_file()] if failed.exists() else []


def errors_log(pipe: Pipeline, ticker: str):
    errors_log_for_parts(pipe.asset_class, ticker, pipe.name)


def errors_log_for_parts(asset_class: str, ticker: str, pipeline_name: str):
    debug = mkdir(pipeline_dir_for_parts(asset_class, ticker, pipeline_name) / "debug")
    return debug / "errors.log"


def extract_ticker_pipeline(child_path: Path) -> tuple[str, str, str]:
    for marker in ("waiting", "ready", "debug"):
        if marker in child_path.parts:
            idx = child_path.parts.index(marker)
            return child_path.parts[idx - 3], child_path.parts[idx - 2], child_path.parts[idx - 1]
    raise ValueError(f"Not a pipeline path: {child_path}")
