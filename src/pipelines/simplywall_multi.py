import asyncio, sys, glob, json, pandas
from src.scheduler import Pipeline, line_task, aggregate_task, line_progress
from src.config import output_root
from src.common.util import mkdir, timestamp
from src.services.proxies import random_proxy
from src.services.browser import new_page, error_name, expect_json_response
from src.common.validate_data import validate_schema

name = 'simplywall_multi'
input_path = 'input/simplywall/sectors.csv'
output_dir = lambda country: mkdir(f'{output_root}/{name}/{country}')
raw_dir = lambda country: mkdir(f'{output_dir(country)}/awaiting-extraction')
aggregated_dir = lambda country: mkdir(f'{output_dir(country)}/ready')


def pipeline(country):
    return Pipeline(
        name=name,
        tasks=[
            line_task(lambda sector: scrape(country, sector), input_path, output_dir(country)),
            # file_task(validate_data, validate_data_input(output_dir(country)),
            aggregate_task(lambda: aggregate(country), input_path, output_dir(country), aggregated_dir(country)),
        ],
        progress=line_progress(input_path, output_dir)
    )


def scrape(country, sector):
    url = f'https://simplywall.st/stocks/{country}/{sector}'
    path = f'{raw_dir(country)}/{sector}-{timestamp()}.json'
    asyncio.run(_scrape(random_proxy(), url, path))


async def _scrape(proxy: str, url: str, path: str):
    print(f'scraping, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with new_page(proxy) as page:
            await expect_json_response(path, page, url, lambda r: "api/grid/filter" in r.url)
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)


def validate_data(country: str, path: str):
    schema = [
        {
            'ticker': str,
            'value': int,
            'future': int,
            'past': int,
            'health': int,
            'income': int,
        }
    ]
    validate_schema(path, schema, output_dir(country))


def aggregate(country):
    raw_files = glob.glob(f'{raw_dir(country)}/*.json')
    all_data = [stock
                for file_path in raw_files
                for stock in _scores_from_file(file_path)]
    sorted_data = sorted(all_data, key=lambda x: x['ticker'])
    df = pandas.DataFrame(sorted_data)
    output_path = f'{aggregated_dir(country)}/{timestamp()}.csv'
    df.to_csv(output_path, index=False)
    return output_path


def _scores_from_file(path):
    with open(path, 'r') as f:
        data = json.load(f)
        return [_scores_from_obj(stock) for stock in data.get('data', [])]


def _scores_from_obj(stock):
    scores = stock['score']['data']
    return {
        'ticker': stock['ticker_symbol'],
        'value': scores['value'],
        'future': scores['future'],
        'past': scores['past'],
        'health': scores['health'],
        'income': scores['income'],
    }

