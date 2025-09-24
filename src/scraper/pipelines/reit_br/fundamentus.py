import asyncio

import pandas

from src.scraper.core import paths_pipe
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import normalization
from src.scraper.core.tasks.base import global_task
from src.scraper.core.tasks.normalization import normalize_csv
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
    path = paths_pipe.for_pipe(pipe, "_global").output_file("normalization", "csv")
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


def _normalize(data: dict) -> dict:
    norm_keys = normalization.traverse_keys(normalization.key)
    remove_keys = normalization.remove_keys("papel", "endereco")
    numbers = normalization.traverse_values(normalization.value)
    magnitude = normalization.traverse_dict(
        {
            "valor_de_mercado": lambda v: v / 1e9,
            "liquidez": lambda v: v / 1e6,
            "preco_do_m2": lambda v: v / 1e3,
        }
    )
    remove_brick = lambda d: _remove_brick_fields(d) if d.get("segmento") == "Títulos e Val. Mob." else d
    return normalization.pipe(norm_keys, remove_keys, numbers, magnitude, remove_brick)(data)


def _remove_brick_fields(d):
    empty_fields = ["qtd_de_imoveis", "vacancia_media", "preco_do_m2", "aluguel_por_m2", "cap_rate"]
    for field in empty_fields:
        if d.get(field) == 0:
            d.pop(field, None)
    return d
