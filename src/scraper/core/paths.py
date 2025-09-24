from dataclasses import dataclass
from pathlib import Path

from src.common.config import data_root
from src.common.util.date_util import timestamp
from src.scraper.core.util.files import mkdir

"""
Path structure per ticker and pipeline:

{asset_class}/
    {ticker}/
        {pipeline}/
            waiting/                # Input for intermediate pipeline stages
                extraction/
                validation/
                normalization/
            ready/                  # Final output, ready to be consumed via API
            debug/                  # Debug information. Also determines when to abort a pipeline.
                failed/             # Failed processing attempts
                    extraction/
                    validation/
                    normalization/
                processed/          # Successfully processed files
                errors.log
"""

_WAITING = "waiting"
_READY = "ready"
_DEBUG = "debug"
_FAILED = "failed"
_PROCESSED = "processed"
_ERRORS_LOG = "errors.log"


@dataclass(frozen=True)
class PipelinePaths:
    asset_class: str
    ticker: str
    pipeline_name: str

    @property
    def base_dir(self) -> Path:
        return Path(data_root) / self.asset_class / self.ticker / self.pipeline_name

    def stage_dir(self, stage: str) -> Path:
        """Get directory for a specific stage (creates if it doesn't exist)."""
        if stage == _READY:
            return mkdir(self.base_dir / _READY)
        return mkdir(self.base_dir / _WAITING / stage)

    @property
    def debug_dir(self) -> Path:
        return mkdir(self.base_dir / _DEBUG)

    def failed_dir(self, stage: str) -> Path:
        return mkdir(self.debug_dir / _FAILED / stage)

    @property
    def processed_dir(self) -> Path:
        return mkdir(self.debug_dir / _PROCESSED)

    def output_file(self, stage: str, ext: str):
        return self.stage_dir(stage) / f"{timestamp()}.{ext}"

    @property
    def errors_log(self) -> Path:
        return self.debug_dir / _ERRORS_LOG

    @property
    def has_waiting_files(self) -> bool:
        """Check if there are any files waiting to be processed."""
        waiting_path = self.base_dir / _WAITING
        return any(f.is_file() for f in waiting_path.rglob("*"))


def for_parts(asset_class: str, ticker: str, pipeline_name: str) -> PipelinePaths:
    """Get path helper for pipeline components."""
    return PipelinePaths(asset_class, ticker, pipeline_name)


def for_child(child_path: Path) -> PipelinePaths:
    """Get path helper from a child path within the pipeline structure."""
    asset_class, ticker, pipeline_name = parts(child_path)
    return for_parts(asset_class, ticker, pipeline_name)


def split_files(input_path: Path, current_stage: str, next_stage: str, out_ext: str | None = None) -> list[Path]:
    """Split files into output, failed, and processed paths."""
    paths = for_child(input_path)
    output_file = f"{input_path.stem}.{out_ext}" if out_ext else input_path.name
    return [
        paths.stage_dir(next_stage) / output_file,
        paths.failed_dir(current_stage) / input_path.name,
        paths.processed_dir / input_path.name,
    ]


def processed_path(input_path: Path) -> Path:
    paths = for_child(input_path)
    return paths.processed_dir / input_path.name


def parts(child_path: Path) -> tuple[str, str, str]:
    """Extract (asset_class, ticker, pipeline_name) from a child path."""
    for marker in (_WAITING, _READY, _DEBUG):
        if marker in child_path.parts:
            idx = child_path.parts.index(marker)
            return child_path.parts[idx - 3], child_path.parts[idx - 2], child_path.parts[idx - 1]
    raise ValueError(f"Not a pipeline path: {child_path}")
