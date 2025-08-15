import csv
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src import config

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


@app.get("/api/scraped")
def get_data():
    yahoo_chart = get_yahoo_chart()
    statusinvest = get_statusinvest()
    yahoo_scraped = get_yahoo_scraped()
    yahoo_api_rec = get_yahoo_api_recom()
    tradingview = get_tradingview()
    simplywall = get_simplywall()

    tickers = set(statusinvest) | set(yahoo_scraped)
    rows = {}

    for ticker in tickers:
        rows[ticker] = {
            **prefix_dict(statusinvest.get(ticker), "statusinvest"),
            **prefix_dict(simplywall.get(ticker), "simplywallst"),
            **prefix_dict(
                yahoo_scraped.get(ticker, {}).get("analyst_rating"), "yahoo_rating"
            ),
            **prefix_dict(
                yahoo_scraped.get(ticker, {}).get("price_forecast"), "yahoo_forecast"
            ),
            **prefix_dict(
                tradingview.get(ticker, {}).get("analyst_rating"), "tradingview_rating"
            ),
            **prefix_dict(
                tradingview.get(ticker, {}).get("price_forecast"), "tradingview_forecast"
            ),
            **prefix_dict(yahoo_api_rec.get(ticker), "yahoo_api_rating"),
            **prefix_dict(yahoo_chart.get(ticker), "yahoo_chart"),
        }

    return JSONResponse(rows)


def get_statusinvest():
    path = pick_latest_file(root_dir / "statusinvest/data/ready")
    return load_csv_all_tickers(path)


def get_yahoo_scraped():
    return extract_json_per_ticker("yahoo/data/ready", lambda d: d)


def get_tradingview():
    return extract_json_per_ticker("tradingview/data/ready", lambda d: d)


def get_yahoo_chart():
    return extract_json_per_ticker(
        "yahoo_chart/data/ready",
        lambda arr: {
            "1mo": arr[-21:],
            "1y": [v for i, v in enumerate(arr[-252:]) if i % 5 == 0],
            "5y": [v for i, v in enumerate(arr) if i % 20 == 0],
        },
    )


def get_yahoo_api_recom():
    return extract_json_per_ticker(
        "yahoo_recommendations/data/ready",
        lambda d: {
            "strongBuy": d.get("strongBuy", {}).get("0"),
            "buy": d.get("buy", {}).get("0"),
            "hold": d.get("hold", {}).get("0"),
            "sell": d.get("sell", {}).get("0"),
            "strongSell": d.get("strongSell", {}).get("0"),
        },
    )


def get_simplywall():
    return extract_json_per_ticker(
        "simplywall/data/ready",
        lambda d: d.get("data", {}).get("Company", {}).get("score"),
    )


def extract_json_per_ticker(subpath: str, extract_fn):
    dir_path = root_dir / subpath
    if not dir_path.exists():
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
                headers[i + 1]: rest[i] for i in range(len(rest))
            }
            data[ticker] = values
    return data


def pick_latest_file(dir_path: Path) -> Path | None:
    if not dir_path.exists():
        return None
    files = sorted(dir_path.iterdir())
    return files[-1] if files else None


def prefix_dict(d: dict, prefix: str):
    if not d:
        return {}
    return {f"{prefix}.{k}": v for k, v in d.items()}
