from datetime import datetime, timedelta
from pathlib import Path

from src.common import config
from src.common.services.repository import query_tickers
from src.common.util.date_util import datetime_from_filename
from src.scraper.core import paths
from src.scraper.core.logs import timestamp_from_log
from src.scraper.core.scheduler import Pipeline, Progress


def progress(pipe: Pipeline, input_domain: set[str]) -> Progress:
    return Progress(
        full_domain=input_domain,
        ready=_ready(pipe, input_domain),
        waiting=_waiting(pipe, input_domain),
        aborted=_aborted(pipe, input_domain),
    )


def intermediate_input(pipe: Pipeline, stage: str) -> set[Path]:
    return {
        file
        for ticker in query_tickers(pipe.asset_class) + ["_global"]
        for file in paths.waiting_files(pipe, ticker, stage)
    }


def has_recent_files(pipe: Pipeline, ticker: str, stage: str) -> bool:
    latest = paths.latest_file(pipe, ticker, stage)
    return latest and datetime_from_filename(latest) > datetime.now() - timedelta(days=config.data_refresh_days)


def _count_total_recent_failures(pipe: Pipeline, ticker: str) -> int:
    return _count_recent_failed_files(pipe, ticker) + _count_recent_error_logs(pipe, ticker)


def _count_recent_failed_files(pipe: Pipeline, ticker: str) -> int:
    cutoff = datetime.now() - timedelta(days=config.data_refresh_days)
    return sum(1 for file in paths.failed_files(pipe, ticker) if datetime_from_filename(file) > cutoff)


def _count_recent_error_logs(pipe: Pipeline, ticker: str) -> int:
    errors = paths.errors_log(pipe, ticker)
    if not errors.exists():
        return 0
    cutoff = datetime.now() - timedelta(days=config.data_refresh_days)
    with errors.open() as file:
        return sum(1 for line in file if timestamp_from_log(line) > cutoff)


def _waiting(pipe: Pipeline, all_tickers: set[str]) -> set[str]:
    return {ticker for ticker in all_tickers if paths.has_waiting_files(pipe, ticker)}


def _ready(pipe: Pipeline, all_tickers: set[str]) -> set[str]:
    return {ticker for ticker in all_tickers if has_recent_files(pipe, ticker, "ready")}


def _aborted(pipe: Pipeline, all_tickers: set[str]) -> set[str]:
    return {ticker for ticker in all_tickers if _should_abort(pipe, ticker)}


def _should_abort(pipe: Pipeline, ticker: str) -> bool:
    return _count_total_recent_failures(pipe, ticker) >= config.error_limit
