from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import csv

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://monitor-de-acoes.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

root_dir = Path("../stocks-scraper/output/20250803")


@app.get("/api/scraped")
def get_data():
    chart = yahoo_chart()
    funds = statusinvest()
    yahoo_scrape = yahoo_scraped()
    yahoo_api_rec = yahoo_api_recom()
    simplywall_data = simplywall()

    tickers = set(funds) | set(yahoo_scrape)
    rows = {}

    for ticker in tickers:
        rows[ticker] = {
            **prefix_dict(funds.get(ticker), "statusinvest"),
            **prefix_dict(simplywall_data.get(ticker), "simplywallst"),
            **prefix_dict(
                yahoo_scrape.get(ticker, {}).get("analyst_rating"), "yahoo_rating"
            ),
            **prefix_dict(
                yahoo_scrape.get(ticker, {}).get("price_forecast"), "yahoo_forecast"
            ),
            **prefix_dict(yahoo_api_rec.get(ticker), "yahoo_api_rating"),
            **prefix_dict(chart.get(ticker), "yahoo_chart"),
        }

    return JSONResponse(rows)


def statusinvest():
    file_path = pick_latest_file(root_dir / "statusinvest/data/ready")
    return parse_statusinvest(file_path) if file_path else {}


statusinvest_header_map = {
    "LIQUIDEZ MEDIA DIARIA": "liquidezMediaDiaria",
    "MARG. LIQUIDA": "margem",
    "DIV. LIQ. / PATRI.": "divida",
    "LIQ. CORRENTE": "liquidezCorrente",
    "CAGR LUCROS 5 ANOS": "lucro",
}


def parse_statusinvest(file_path: Path):
    data = {}
    with file_path.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        headers = next(reader)
        headers = [
            statusinvest_header_map.get(h.strip(), h.strip())
            for h in headers
        ]
        for row in reader:
            ticker, *rest = row
            values = {
                headers[i + 1]: try_convert_number(rest[i])
                for i in range(len(rest))
            }
            data[ticker] = values
    return data


def try_convert_number(value: str):
    try:
        return float(value.replace(".", "").replace(",", "."))
    except ValueError:
        return value


def yahoo_scraped():
    return extract_json_per_ticker("yahoo/data/ready", lambda d: d)


def yahoo_chart():
    return extract_json_per_ticker(
        "yahoo_chart/data/ready",
        lambda arr: {
            "1mo": arr[-21:],
            "1y": [v for i, v in enumerate(arr[-252:]) if i % 5 == 0],
            "5y": [v for i, v in enumerate(arr) if i % 20 == 0],
        },
    )


def yahoo_api_recom():
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


def simplywall():
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


def pick_latest_file(dir_path: Path) -> Path | None:
    if not dir_path.exists():
        return None
    files = sorted(dir_path.iterdir())
    return files[-1] if files else None


def prefix_dict(d: dict, prefix: str):
    if not d:
        return {}
    return {f"{prefix}.{k}": v for k, v in d.items()}
