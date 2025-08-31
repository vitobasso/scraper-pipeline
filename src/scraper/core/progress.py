from datetime import datetime, timedelta
from pathlib import Path

from src.common import config
from src.common.services.repository import query_tickers
from src.common.util.date_util import datetime_from_filename
from src.scraper.core import paths
from src.scraper.core.logs import timestamp_from_log
from src.scraper.core.scheduler import Progress


def progress(pipeline: str, input_domain: set[str]) -> Progress:
    return Progress(
        full_domain=input_domain,
        ready=_ready(pipeline, input_domain),
        waiting=_waiting(pipeline, input_domain),
        aborted=_aborted(pipeline, input_domain),
    )


def intermediate_input(pipeline: str, stage: str) -> set[Path]:
    return {file for ticker in query_tickers() + ["_global"] for file in paths.waiting_files(ticker, pipeline, stage)}


def has_recent_files(ticker: str, pipeline: str, stage: str) -> bool:
    latest = paths.latest_file(ticker, pipeline, stage)
    return latest and datetime_from_filename(latest) > datetime.now() - timedelta(days=config.data_refresh_days)


def _count_total_recent_failures(ticker: str, pipeline: str) -> int:
    return _count_recent_failed_files(ticker, pipeline) + _count_recent_error_logs(ticker, pipeline)


def should_abort(ticker: str, pipeline: str) -> bool:
    return _count_total_recent_failures(ticker, pipeline) >= config.error_limit


def _count_recent_failed_files(ticker: str, pipeline: str) -> int:
    cutoff = datetime.now() - timedelta(days=config.data_refresh_days)
    return sum(1 for file in paths.failed_files(ticker, pipeline) if datetime_from_filename(file) > cutoff)


def _count_recent_error_logs(ticker: str, pipeline: str) -> int:
    errors = paths.errors_log(pipeline, ticker)
    if not errors.exists():
        return 0
    cutoff = datetime.now() - timedelta(days=config.data_refresh_days)
    with errors.open() as file:
        return sum(1 for line in file if timestamp_from_log(line) > cutoff)


def _waiting(pipeline: str, all_tickers: set[str]) -> set[str]:
    return {ticker for ticker in all_tickers if paths.has_waiting_files(ticker, pipeline)}


def _ready(pipeline: str, all_tickers: set[str]) -> set[str]:
    return {ticker for ticker in all_tickers if has_recent_files(ticker, pipeline, "ready")}


def _aborted(pipeline: str, all_tickers: set[str]) -> set[str]:
    return {ticker for ticker in all_tickers if should_abort(ticker, pipeline)}
