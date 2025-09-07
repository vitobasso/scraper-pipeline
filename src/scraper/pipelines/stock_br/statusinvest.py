import asyncio

from src.scraper.core import paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import normalization
from src.scraper.core.tasks.base import global_task
from src.scraper.core.tasks.normalization import normalize_csv
from src.scraper.services.browser import click, click_download, error_name, page_goto
from src.scraper.services.proxies import random_proxy


def pipeline():
    return Pipeline.from_caller(
        tasks=[
            global_task(sync_download),
            normalize_csv(_normalize, delimiter=";"),
        ],
    )


def sync_download(pipe: Pipeline):
    asyncio.run(_download(pipe))


async def _download(pipe: Pipeline):
    path = paths.for_pipe(pipe, "_global").output_file("normalization", "csv")
    proxy = random_proxy(pipe)
    url = "https://statusinvest.com.br/acoes/busca-avancada"
    print(f"downloading csv, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url) as page:
            await click(page, "button", "Buscar")
            await click_download(path, page, "a", "DOWNLOAD")
    except Exception as e:
        log(error_name(e), "_global", pipe)


def _normalize(data: dict) -> dict:
    keys = normalization.traverse_keys(normalization.key)
    values = normalization.traverse_values(normalization.value)
    magnitude = normalization.traverse_dict(
        {
            "liquidez_media_diaria": lambda v: v / 1e6,
            "valor_de_mercado": lambda v: v / 1e9,
        }
    )
    return normalization.pipe(keys, values, magnitude)(data)
