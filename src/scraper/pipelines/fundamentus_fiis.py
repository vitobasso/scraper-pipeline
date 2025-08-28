import asyncio
from pathlib import Path

import pandas

from src.common.util import timestamp
from src.scraper.core import normalization, paths
from src.scraper.core.logs import log
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import global_task
from src.scraper.services.browser import error_name, page_goto
from src.scraper.services.proxies import random_proxy

name = "fundamentus_fiis"


def pipeline():
    return Pipeline(
        name=name,
        tasks=[global_task(name, scrape)],  # TODO normalize, like statusinvest
    )


def scrape():
    url = "https://www.fundamentus.com.br/fii_resultado.php"
    path = paths.stage_dir_for("_global", name, "ready") / f"{timestamp()}.csv"
    proxy = random_proxy(name)
    asyncio.run(_scrape(proxy, url, path))


async def _scrape(proxy: str, url: str, path: Path):
    print(f"scraping html, url: {url}, path: {path}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url, wait_until="domcontentloaded") as page:
            await page.wait_for_selector("#tabelaResultado")
            rows = await page.locator("#tabelaResultado tbody tr").all()
            data = [await _extract_row(row) for row in rows]
            df = pandas.DataFrame(data, columns=headers)
            df.to_csv(path, index=False)
    except Exception as e:
        log(error_name(e), "_global", name)


async def _extract_row(row):
    cells = await row.locator("td").all_text_contents()
    if cells:
        return [normalization.value(c) for c in cells[:-1]]
    else:
        return None


headers = [
    "ticker",
    "segmento",
    "cotação",
    "ffo yield",
    "dividend yield",
    "p/vp",
    "valor de mercado",
    "liquidez",
    "qtd de imóveis",
    "preço do m2",
    "aluguel por m2",
    "cap rate",
    "vacância média",
]
