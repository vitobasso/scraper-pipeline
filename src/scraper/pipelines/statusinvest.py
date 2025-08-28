import asyncio
import csv
import json
from pathlib import Path

from src.common import config, repository
from src.common.util import timestamp
from src.scraper.core import normalization, paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import global_task, intermediate_task
from src.scraper.services.browser import click, click_download, error_name, page_goto
from src.scraper.services.proxies import random_proxy

name = "statusinvest"
pipe_dir = paths.pipeline_dir("_global", name)


def pipeline():
    return Pipeline(
        name=name,
        tasks=[
            global_task(name, sync_download),
            intermediate_task(normalize, name, "normalization"),
        ],
    )


def sync_download():
    asyncio.run(download())


async def download():
    path = paths.stage_dir(pipe_dir, "normalization") / f"{timestamp()}.csv"
    return await _download(random_proxy(name), path)


async def _download(proxy: str, path: Path):
    url = "https://statusinvest.com.br/acoes/busca-avancada"
    print(f"downloading csv, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url) as page:
            await click(page, "button", "Buscar")
            await click_download(path, page, "a", "DOWNLOAD")
    except Exception as e:
        log(error_name(e), "_global", name)


def normalize(path: Path):
    print(f"normalizing, path: {path}")
    try:
        _normalize(path)
        output, _, processed = paths.split_files(path, "normalization", "ready", "stamp")
        path.rename(processed)
        output.touch()
    except Exception as e:
        log(str(e), "_global", name)


def _normalize(input_file: Path):
    requested_tickers = set(repository.query_tickers())
    with input_file.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        headers = next(reader)
        headers = [normalization.key(h) for h in headers]

        for row in reader:
            ticker, *rest = row
            if config.only_requested_tickers and ticker not in requested_tickers:
                continue
            values = [normalization.value(v) for v in rest]
            data = dict(zip(headers, [ticker] + values, strict=False))

            out_path = paths.stage_dir_for(ticker, name, "ready") / f"{input_file.stem}.json"
            with out_path.open("w", encoding="utf-8") as out:
                json.dump(data, out, ensure_ascii=False, indent=2)
