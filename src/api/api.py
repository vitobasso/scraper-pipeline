import csv
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api import schemas

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

root_dir = Path("output")


@app.get("/api/scraped")
def get_meta():
    return {
        "versions": get_versions(),
        "schema": schemas.all
    }


def get_versions():
    if not root_dir.exists():
        return []
    return sorted([p.name for p in root_dir.iterdir() if p.is_dir()])


@app.get("/api/scraped/{version}")
def get_data(version: str):
    base_dir = root_dir / version
    if not base_dir.exists():
        raise HTTPException(status_code=404)
    yahoo_chart = get_yahoo_chart(base_dir)
    statusinvest = get_statusinvest(base_dir)
    yahoo_scraped = get_yahoo_scraped(base_dir)
    yahoo_api_rec = get_yahoo_api_recom(base_dir)
    tradingview = get_tradingview(base_dir)
    simplywall = get_simplywall(base_dir)

    tickers = set(statusinvest) | set(yahoo_scraped)
    rows = {}

    for ticker in tickers:
        rows[ticker] = {
            **prefix_dict(statusinvest.get(ticker), "statusinvest"),
            **prefix_dict(simplywall.get(ticker), "simplywallst"),
            **prefix_dict(yahoo_scraped.get(ticker, {}).get("analyst_rating"), "yahoo_rating"),
            **prefix_dict(yahoo_scraped.get(ticker, {}).get("price_forecast"), "yahoo_forecast"),
            **prefix_dict(tradingview.get(ticker, {}).get("analyst_rating"), "tradingview_rating"),
            **prefix_dict(tradingview.get(ticker, {}).get("price_forecast"), "tradingview_forecast"),
            **prefix_dict(yahoo_api_rec.get(ticker), "yahoo_api_rating"),
            **prefix_dict(yahoo_chart.get(ticker), "yahoo_chart"),
        }

    return JSONResponse(rows)


def get_statusinvest(base_dir: Path):
    path = pick_latest_file(base_dir / "statusinvest/data/ready")
    return load_csv_all_tickers(path)


def get_yahoo_scraped(base_dir: Path):
    return extract_json_per_ticker(base_dir / "yahoo/data/ready", lambda d: d)


def get_tradingview(base_dir: Path):
    return extract_json_per_ticker(base_dir / "tradingview/data/ready", lambda d: d)


def get_yahoo_chart(base_dir: Path):
    return extract_json_per_ticker(
        base_dir / "yahoo_chart/data/ready",
        lambda arr: {
            "1mo": arr[-21:],
            "1y": [v for i, v in enumerate(arr[-252:]) if i % 5 == 0],
            "5y": [v for i, v in enumerate(arr) if i % 20 == 0],
        },
    )


def get_yahoo_api_recom(base_dir: Path):
    return extract_json_per_ticker(
        base_dir / "yahoo_recommendations/data/ready",
        lambda d: {
            "strongBuy": d.get("strongBuy", {}).get("0"),
            "buy": d.get("buy", {}).get("0"),
            "hold": d.get("hold", {}).get("0"),
            "sell": d.get("sell", {}).get("0"),
            "strongSell": d.get("strongSell", {}).get("0"),
        },
    )


def get_simplywall(base_dir: Path):
    return extract_json_per_ticker(
        base_dir / "simplywall/data/ready",
        lambda d: d.get("data", {}).get("Company", {}).get("score"),
    )


def extract_json_per_ticker(dir_path: Path, extract_fn):
    if not dir_path or not dir_path.exists():
        return {}
    result = {}
    for file in dir_path.iterdir():
        ticker = file.name.split("-")[0].upper()
        with file.open(encoding="utf-8") as f:
            content = json.load(f)
        result[ticker] = extract_fn(content)
    return result


def load_csv_all_tickers(path: Path):
    if not path or not path.exists():
        return {}
    data = {}
    with path.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        headers = next(reader)
        for row in reader:
            ticker, *rest = row
            values = {
                headers[i + 1]: try_float(rest[i]) for i in range(len(rest))
            }
            data[ticker] = values
    return data


def try_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return val


def pick_latest_file(dir_path: Path) -> Path | None:
    if not dir_path.exists():
        return None
    files = sorted(dir_path.iterdir())
    return files[-1] if files else None


def prefix_dict(d: dict, prefix: str):
    if not d:
        return {}
    return {f"{prefix}.{k}": v for k, v in d.items()}
