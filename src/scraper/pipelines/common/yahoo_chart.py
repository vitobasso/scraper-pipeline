import yfinance
from curl_cffi import requests

from src.common import config
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks.api_call import call_api
from src.scraper.core.tasks.normalization import normalize_json
from src.scraper.core.tasks.validation import validate_json


def from_caller():
    return Pipeline.from_caller(
        stack_frame_index=2,
        tasks=[
            call_api(call),
            validate_json(validator),
            normalize_json(normalize),
        ],
    )


def call(ticker: str, proxy: str):
    session = requests.Session(impersonate="chrome", verify=config.enforce_https)
    result = yfinance.Ticker(f"{ticker}.SA", session=session).history(
        period="5y", interval="1d", proxy=proxy, raise_errors=True
    )
    return result["Close"].tolist()


# business days
MONTH_DAYS = 21
YEAR_DAYS = 252

# raw data expected to have 5 years of data in days, with 10% tolerance
TOLERANCE_MIN = 5 * YEAR_DAYS * 0.9
TOLERANCE_MAX = 5 * YEAR_DAYS * 1.1


def validator(data):
    if not data:
        return ["array is empty"]
    elif len(data) < TOLERANCE_MIN or len(data) > TOLERANCE_MAX:
        return [f"expected between {TOLERANCE_MIN} and {TOLERANCE_MAX} days of data, got {len(data)}"]
    else:
        return []


def normalize(raw):
    avg = lambda start, end: sum(raw[start:end]) / (end - start)
    var = lambda a1, a2, b1, b2: (avg(b1, b2) - avg(a1, a2)) / avg(a1, a2)
    return {
        "1mo_series": raw[-21:],
        "1y_series": [v for i, v in enumerate(raw[-252:]) if i % 5 == 0],
        "5y_series": [v for i, v in enumerate(raw) if i % 20 == 0],
        "1mo_variation": var(-MONTH_DAYS - 1, -MONTH_DAYS + 1, -3, -1),
        "1y_variation": var(-YEAR_DAYS - 12, -YEAR_DAYS + 12, -25, -1),
        "5y_variation": var(0, 100, -100, -1),
    }
