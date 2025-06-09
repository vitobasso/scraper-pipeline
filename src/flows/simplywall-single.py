import asyncio, sys, json
from src.scheduler import Pipeline, line_task, file_task
from src.config import output_root
from src.core.util import timestamp, mkdir
from src.core.proxies import random_proxy
from src.core.browser_session import new_page, error_name, load_timeout
from src.flows.generic.extract_data import ask
from src.flows.generic.validate_data import validate, input_dir as validate_data_input

name = 'simplywall-single'
output_dir = mkdir(f'{output_root}/{name}')
urls_path = lambda t: mkdir(f'{output_dir}/setup/urls-{t}.csv')
raw_dir = mkdir(f'{output_dir}/raw')


def pipeline(input_path: str) -> Pipeline:
    return {
        'name': name,
        'tasks': [
            line_task(scrape, input_path, output_dir),
            # file_task(lambda path: validate_raw(path, output_dir), validate_raw_input(output_dir)),
            # file_task(extract_data, extract_data_input(output_dir)),
            file_task(validate_data, validate_data_input(output_dir)),
        ]
    }


# TODO gemini-flash doesn't seem to work, gemini-pro gets most urls right
def find_urls(input_path):
    tickers = ''  # TODO load from input_path
    path = urls_path(timestamp())
    prompt = f"""
    Find the url in simplywall.st for each ticker below:
    {tickers}

    Return as pure CSV with columns: ticker, url
    Do not use any markdown formatting or backticks
    """
    ask(prompt, path)


def scrape(ticker):
    url = f'https://simplywall.st/stocks/br/banks/bovespa-{ticker}/banco-do-brasil-shares'
    path = f'{raw_dir}/{ticker}-{timestamp()}.json'
    asyncio.run(_scrape(random_proxy(), url, path))


async def _scrape(proxy: str, url: str, path: str):
    print(f'scraping, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with new_page(proxy) as page:
            match_request = lambda r: "/graphql" in r.url and "CompanySummary" in (r.request.post_data or "")
            async with page.expect_response(match_request) as response_info:
                await page.goto(url, timeout=load_timeout, wait_until='domcontentloaded')
            response = await response_info.value
            data = await response.json()
            with open(path, 'w') as f:
                json.dump(data, f)
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)


def validate_data(path: str):
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
    validate(path, schema, raw_dir)

