import asyncio, sys, csv

from src.common.logs import log
from src.scheduler import Pipeline, line_task, file_task, line_progress
from src.config import output_root
from src.common.util import timestamp, mkdir
from src.services.proxies import random_proxy
from src.services.browser import new_page, error_name, expect_json_response
from src.common.extract_data import ask
from src.common.validate_data import validate_schema, input_dir as validate_data_input, valid_data_dir

name = 'simplywall'
output_dir = mkdir(f'{output_root}/{name}')
completed_dir = valid_data_dir(output_dir)
urls_path = 'input/simplywall/urls.csv'


def pipeline(input_path: str):
    return Pipeline(
        name=name,
        tasks=[
            line_task(scrape, input_path, output_dir),
            file_task(validate_data, validate_data_input(output_dir)),
        ],
        progress=line_progress(input_path, output_dir)
    )


def scrape(ticker):
    url = get_url(ticker)
    if not url:
        print(f'failed: simplywall.st url missing for {ticker}', file=sys.stderr)
    path = f'{completed_dir}/{ticker}-{timestamp()}.json'
    asyncio.run(_scrape(random_proxy(), url, path, ticker))


async def _scrape(proxy: str, url: str, path: str, ticker: str):
    print(f'scraping, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with new_page(proxy) as page:
            match_request = lambda r: "/graphql" in r.url and "CompanySummary" in (r.request.post_data or "")
            await expect_json_response(path, page, url, match_request)
    except Exception as e:
        log(error_name(e), name, ticker)


# TODO data/Company/data
def validate_data(path: str):
    schema = [
        {
            'ticker': str,
            'value': int,
            'future': int,
            'past': int,
            'health': int,
            'dividend': int,
        }
    ]
    validate_schema(path, schema, completed_dir)


def get_url(ticker):
    with open(urls_path) as f:
        for row in csv.reader(f):
            if row[0].lower() == ticker.lower():
                return row[1]
    return None

# TODO gemini-flash doesn't seem to work, gemini-pro gets most urls right
def discover_urls(input_path):
    path = f'{urls_path}-{timestamp()}'
    with open(input_path, 'r') as f:
        tickers = [line.strip() for line in f.readlines()]
        prompt = f"""
        Find the url in simplywall.st for each ticker below:
        {tickers}
    
        Return as pure CSV with columns: ticker, url
        Their urls are formated as follows: https://simplywall.st/stocks/br/<sector>/bovespa-<ticker>/<slug>
        You'll need to find the sector and slug for each ticker in order to compose the url
    
        E.g.: 
        BBAS3,https://simplywall.st/stocks/br/banks/bovespa-bbas3/banco-do-brasil-shares
        TAEE11,https://simplywall.st/stocks/br/utilities/bovespa-taee11/transmissora-alianca-de-energia-eletrica-shares
        GGBR4,https://simplywall.st/stocks/br/materials/bovespa-ggbr4/gerdau-shares
        """
        ask(prompt, path)
