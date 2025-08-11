import json
import yfinance

from src.common.logs import log
from src.common.util import mkdir, timestamp
from src.common.validate_data import validate_json, input_dir as validate_data_input, valid_data_dir
from src.config import output_root
from src.scheduler import Pipeline, line_task, file_task, line_progress
from src.services.proxies import random_proxy

name = 'yahoo_chart'
output_dir = mkdir(f'{output_root}/{name}')
data_dir = mkdir(f'{output_dir}/data/awaiting-validation')
completed_dir = valid_data_dir(output_dir)


def pipeline(input_path: str):
    return Pipeline(
        name=name,
        tasks=[
            line_task(call_api, input_path, output_dir),
            file_task(validate_data, validate_data_input(output_dir)),
        ],
        progress=line_progress(input_path, output_dir)
    )


def call_api(ticker):
    proxy = random_proxy()
    path = f'{data_dir}/{ticker}-{timestamp()}.json'
    print(f'scraping, ticker: {ticker}, path: {path}, proxy: {proxy}')
    try:
        result = yfinance.Ticker(f'{ticker}.SA').history(period="5y", interval="1d", proxy=proxy, raise_errors=True)
        data = result["Close"].tolist()
        with open(path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        log(str(e), name, ticker)


def validate_data(path: str):
    validator = lambda data: ["array is empty"] if not data else []
    validate_json(path, validator, output_dir)
