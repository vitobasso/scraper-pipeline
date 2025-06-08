import datetime, asyncio, sys, json
from src.scheduler import Pipeline, seed_task, file_task
from src.config import output_root
from src.core.util import mkdir
from src.core.proxies import random_proxy
from src.core.browser_session import browser_page2, error_name, load_timeout
from src.flows.generic.validate_data import validate, input_dir as validate_data_input


name = 'simplywall'
output_dir = f'{output_root}/{name}'
download_dir = mkdir(f'{output_dir}/downloads/awaiting-extraction')


def pipeline() -> Pipeline:
    return {
        'name': name,
        'tasks': [
            # TODO pagination
            # TODO add output dir to know when to stop
            seed_task(scrape),
            file_task(validate_data, validate_data_input(output_dir)),
        ]
    }


def scrape():
    asyncio.run(_scrape(*params('https://simplywall.st/stocks/br/top-gainers')))


async def _scrape(proxy: str, url: str, path: str):
    print(f'scraping, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with browser_page2(proxy) as page:
            async with page.expect_response(lambda r: "api/grid/filter" in r.url) as response_info:
                await page.goto(url, timeout=load_timeout, wait_until='domcontentloaded')
            response = await response_info.value
            data = await response.json()
            with open(path, 'w') as f:
                json.dump(data, f)
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)


def params(url: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    output_path = f'{download_dir}/{timestamp}.json'
    proxy = random_proxy()
    return proxy, url, output_path


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
    validate(path, schema, output_dir)
