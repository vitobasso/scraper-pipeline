import json
from datetime import timedelta, date
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src import config
from src.api import schema
from src.core import util
from src.services import repository, ipc_signal

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

root_dir = Path(config.output_root)


@app.get("/schema")
def get_meta():
    return {
        "schema": schema.all
    }


def default_start(end: date = None):
    return (end or date.today()) - timedelta(days=30)


@app.get("/data")
def get_data(
        tickers: str = Query(..., description="Comma-separated tickers"),
        start: date = Query(default_factory=default_start, description="Start of date range"),
        end: date = Query(date.today(), description="End of the date range"),
):
    tickers_list = tickers.split(",")
    repository.upsert_tickers(tickers_list)
    ipc_signal.wake_scraper()
    return _load_data(tickers_list, start, end)


def _load_data(tickers, start, end):
    results = {}
    for ticker in tickers:
        ticker_data = _get_ticker_data(ticker, start, end)
        if ticker_data:
            results[ticker] = ticker_data
    return results


def _get_ticker_data(ticker: str, start: date, end: date):
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


def _select_file(ready_dir: Path, start: date, end: date):
    candidates = [
        f for f in ready_dir.glob("*.json")
        if start <= util.date_from_filename(f) <= end
    ]
    return max(candidates, key=util.date_from_filename) if candidates else None


def _flatten(d, parent_key=""):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(_flatten(v, new_key))
        else:
            items[new_key] = v
    return items
