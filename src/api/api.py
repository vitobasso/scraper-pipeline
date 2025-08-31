import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from src.api.metadata import labels, schema, sources
from src.common import config
from src.common.services import data, ipc_signal, repository
from src.common.util import date_util

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://monitor-de-acoes.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

optional = Query(None)

root_dir = Path(config.data_root)


@app.get("/meta")
def get_meta():
    return {
        "schema": schema.all,
        "sources": sources.all,
        "labels": labels.all,
        "tickers": data.known_tickers(),
    }


@app.get("/data")
def get_data(
    tickers: str,
    start: date | None = None,
    end: date | None = None,
) -> dict[str, Any]:
    tickers = _validate_tickers(tickers)
    start, end = _validate_period(start, end)
    repository.upsert_tickers(tickers)
    ipc_signal.wake_scraper()
    return _load_data(tickers, start, end)


def _load_data(tickers, start, end) -> dict[str, Any]:
    results = {}
    for ticker in tickers:
        ticker_data = _get_ticker_data(ticker, start, end)
        if ticker_data:
            results[ticker] = ticker_data
    return results


def _get_ticker_data(ticker: str, start: date, end: date) -> dict[str, Any] | None:
    ticker_path = root_dir / ticker
    if not ticker_path.exists():
        return None
    pipelines = {}
    for pipeline_dir in ticker_path.iterdir():
        pipeline_data = _get_pipeline_data(pipeline_dir, start, end)
        if pipeline_data:
            pipelines[pipeline_dir.name] = pipeline_data
    if not pipelines:
        return None
    return _flatten(pipelines)


def _get_pipeline_data(pipeline_dir: Path, start: date, end: date):
    ready_dir = pipeline_dir / "ready"
    if not ready_dir.exists():
        return None
    file = _select_file(ready_dir, start, end)
    if not file:
        return None
    with file.open(encoding="utf-8") as f:
        return json.load(f)


def _select_file(ready_dir: Path, start: date, end: date) -> Path | None:
    candidates = [f for f in ready_dir.glob("*.json") if start <= date_util.date_from_filename(f) <= end]
    return max(candidates, key=date_util.date_from_filename) if candidates else None


def _flatten(d, parent_key="") -> dict[str, Any]:
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(_flatten(v, new_key))
        else:
            items[new_key] = v
    return items


def _validate_tickers(tickers: str) -> list[str]:
    tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not tickers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tickers provided",
        )
    pattern = re.compile(r"^[A-Z0-9]{4}[0-9]{1,2}$")
    return [t for t in tickers if pattern.match(t)]


def _validate_period(start: date, end: date) -> tuple[date, date]:
    end = end or date.today()
    start = start or end - timedelta(days=30)
    if end < start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be later than start date",
        )
    return start, end
