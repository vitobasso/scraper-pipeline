import asyncio

from src.common.util.date_util import timestamp
from src.scraper.core import normalization, paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import global_task, normalize_csv
from src.scraper.services.browser import click, click_download, error_name, page_goto
from src.scraper.services.proxies import random_proxy


def pipeline():
    return Pipeline.from_caller(
        tasks=[
            global_task(sync_download),
            normalize_csv(_normalize),
        ],
    )


def sync_download(pipe: Pipeline):
    asyncio.run(_download(pipe))


async def _download(pipe: Pipeline):
    path = paths.for_pipe(pipe, "_global").stage_dir("normalization") / f"{timestamp()}.csv"
    proxy = random_proxy(pipe)
    url = "https://statusinvest.com.br/acoes/busca-avancada"
    print(f"downloading csv, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url) as page:
            await click(page, "button", "Buscar")
            await click_download(path, page, "a", "DOWNLOAD")
    except Exception as e:
        log(error_name(e), "_global", pipe)


def _normalize(data):
    norm_keys = normalization.traverse_keys(normalization.key)
    numbers = normalization.traverse_values(normalization.value)
    return normalization.pipe(norm_keys, numbers)(data)
