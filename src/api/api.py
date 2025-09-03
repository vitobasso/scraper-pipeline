import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from src.api.metadata.reit_br import labels as reit_labels
from src.api.metadata.reit_br import schema as reit_schema
from src.api.metadata.reit_br import sources as reit_sources
from src.api.metadata.stock_br import labels as stock_labels
from src.api.metadata.stock_br import schema as stock_schema
from src.api.metadata.stock_br import sources as stock_sources
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
        "stock_br": {
            "schema": stock_schema.all,
            "sources": stock_sources.all,
            "labels": stock_labels.all,
            "tickers": data.known_tickers("stock_br"),
        },
        "reit_br": {
            "schema": reit_schema.all,
            "sources": reit_sources.all,
            "labels": reit_labels.all,
            "tickers": data.known_tickers("reit_br"),
        },
    }


@app.get("/data")
def get_data(
    stock_br: str | None = None,
    reit_br: str | None = None,
    start: date | None = None,
    end: date | None = None,
) -> dict[str, Any]:
    start, end = _validate_period(start, end)
    stock_br, reit_br = _process_tickers(stock_br, reit_br)
    ipc_signal.wake_scraper()
    return {
        "stock_br": _load_data("stock_br", stock_br, start, end),
        "reit_br": _load_data("reit_br", reit_br, start, end),
    }


def _load_data(asset_class: str, tickers, start, end) -> dict[str, Any]:
    results = {}
    for ticker in tickers:
        ticker_data = _get_ticker_data(asset_class, ticker, start, end)
        if ticker_data:
            results[ticker] = ticker_data
    return results


def _get_ticker_data(asset_class: str, ticker: str, start: date, end: date) -> dict[str, Any] | None:
    ticker_path = root_dir / asset_class / ticker
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


def _process_tickers(stock_br: str, reit_br: str) -> tuple[list[str], list[str]]:
    stock_br = _validate_stock_br(stock_br)
    reit_br = _validate_reit_br(reit_br)
    if not stock_br and not reit_br:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of 'stock_br' or 'reit_br' is required",
        )
    repository.upsert_tickers(stock_br, "stock_br")
    repository.upsert_tickers(reit_br, "reit_br")
    return stock_br, reit_br


def _validate_stock_br(tickers: str) -> list[str]:
    return _validate_tickers(tickers, re.compile(r"^[A-Z0-9]{4}[0-9]{1,2}$"))


def _validate_reit_br(tickers: str) -> list[str]:
    return _validate_tickers(tickers, re.compile(r"^[A-Z]{4}11$"))


def _validate_tickers(tickers: str, pattern: re.Pattern) -> list[str]:
    tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()] if tickers else []
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
