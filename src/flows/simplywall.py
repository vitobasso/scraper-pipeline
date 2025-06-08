import asyncio, sys, json
from src.scheduler import Pipeline, seed_task, file_task
from src.config import output_root
from src.core.util import mkdir, timestamp
from src.core.proxies import random_proxy
from src.core.browser_session import new_page, error_name, load_timeout
from src.flows.generic.validate_data import validate, input_dir as validate_data_input


name = 'simplywall'
output_dir = f'{output_root}/{name}'
raw_dir = mkdir(f'{output_dir}/raw')
ready_dir = mkdir(f'{output_dir}/ready')


def pipeline() -> Pipeline:
    return {
        'name': name,
        'tasks': [
            # TODO pagination
            # TODO add output dir to know when to stop
            seed_task(scrape, output_dir),
            file_task(validate_data, validate_data_input(output_dir)),
        ]
    }


def scrape():
    path = f'{raw_dir}/{timestamp()}.json'
    asyncio.run(_scrape(random_proxy(), 'https://simplywall.st/stocks/br/top-gainers', path))


async def _scrape(proxy: str, url: str, path: str):
    print(f'scraping, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with new_page(proxy) as page:
            async with page.expect_response(lambda r: "api/grid/filter" in r.url) as response_info:
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
            'dividend': int,
        }
    ]
    validate(path, schema, output_dir)
