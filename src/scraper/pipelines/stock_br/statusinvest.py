import asyncio
import csv
import json
from pathlib import Path

from src.common import config
from src.common.services import repository
from src.common.util.date_util import timestamp
from src.scraper.core import normalization, paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import global_task, intermediate_task
from src.scraper.services.browser import click, click_download, error_name, page_goto
from src.scraper.services.proxies import random_proxy


def pipeline():
    return Pipeline.from_caller(
        tasks=[
            global_task(sync_download),
            intermediate_task(normalize, "normalization"),
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


def normalize(pipe: Pipeline, path: Path):
    print(f"normalizing, path: {path}")
    try:
        _normalize(pipe, path)
        output, _, processed = paths.split_files(path, "normalization", "ready", "stamp")
        path.rename(processed)
        output.touch()
    except Exception as e:
        log(str(e), "_global", pipe)


def _normalize(pipe: Pipeline, input_file: Path):
    requested_tickers = set(repository.query_tickers(pipe.asset_class))
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

            out_path = paths.for_pipe(pipe, ticker).stage_dir("ready") / f"{input_file.stem}.json"
            with out_path.open("w", encoding="utf-8") as out:
                json.dump(data, out, ensure_ascii=False, indent=2)
