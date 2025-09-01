import asyncio

import pandas

from src.common.util.date_util import timestamp
from src.scraper.core import normalization, paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import global_task, normalize_csv
from src.scraper.services.browser import error_name, page_goto
from src.scraper.services.proxies import random_proxy


def pipeline():
    return Pipeline.from_caller(
        tasks=[
            global_task(scrape),
            normalize_csv(_normalize),
        ],
    )


def scrape(pipe: Pipeline):
    asyncio.run(_scrape(pipe))


async def _scrape(pipe: Pipeline):
    url = "https://www.fundamentus.com.br/fii_resultado.php"
    path = paths.stage_dir_for(pipe, "_global", "normalization") / f"{timestamp()}.csv"
    proxy = random_proxy(pipe)
    print(f"scraping html, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url, wait_until="domcontentloaded") as page:
            await page.wait_for_selector("#tabelaResultado")
            page_headers = await page.locator("#tabelaResultado thead tr th").all_text_contents()
            rows = await page.locator("#tabelaResultado tbody tr").all()
            data = [await row.locator("td").all_text_contents() for row in rows]
            df = pandas.DataFrame(data, columns=page_headers)
            df.to_csv(path, index=False)
    except Exception as e:
        log(error_name(e), "_global", pipe)


def _normalize(data) -> str:
    norm_keys = normalization.traverse_keys(normalization.key)
    remove_keys = normalization.remove_keys("papel", "endereco")
    numbers = normalization.traverse_values(normalization.value)
    magnitude = normalization.traverse_dict(
        {
            "valor_de_mercado": lambda v: v / 1_000_000_000,
            "liquidez": lambda v: v / 1_000_000,
            "preco_do_m2": lambda v: v / 1000,
        }
    )
    return normalization.pipe(norm_keys, remove_keys, numbers, magnitude)(data)
