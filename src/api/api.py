import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src.api.metadata import labels, schema, sources
from src.common import config, ipc_signal, repository, util

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

root_dir = Path(config.output_root)


@app.get("/meta")
def get_meta():
    return {
        "schema": schema.all,
        "sources": sources.all,
        "labels": labels.all,
    }


@app.get("/data")
def get_data(
    tickers: str,
    start: date | None = optional,
    end: date | None = optional,
) -> dict[str, Any]:
    end = end or date.today()
    start = start or end - timedelta(days=30)
    tickers = tickers.split(",")
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
    candidates = [f for f in ready_dir.glob("*.json") if start <= util.date_from_filename(f) <= end]
    return max(candidates, key=util.date_from_filename) if candidates else None


def _flatten(d, parent_key="") -> dict[str, Any]:
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(_flatten(v, new_key))
        else:
            items[new_key] = v
    return items
