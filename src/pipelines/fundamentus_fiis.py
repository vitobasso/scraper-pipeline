import asyncio
from pathlib import Path

import pandas

from src.core import paths
from src.core.logs import log
from src.core.scheduler import Pipeline
from src.core.tasks import global_task
from src.core.util import timestamp
from src.services.browser import page_goto, error_name
from src.services.proxies import random_proxy

name = 'fundamentus_fiis'


def pipeline():
    return Pipeline(
        name=name,
        tasks=[global_task(name, scrape)],  # TODO normalize, like statusinvest
    )


def scrape():
    url = 'https://www.fundamentus.com.br/fii_resultado.php'
    path = paths.stage_dir_for("_global", name, "ready") / f'{timestamp()}.csv'
    proxy = random_proxy(name)
    asyncio.run(_scrape(proxy, url, path))


async def _scrape(proxy: str, url: str, path: Path):
    print(f'scraping html, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with page_goto(proxy, url, wait_until='domcontentloaded') as page:
            await page.wait_for_selector("#tabelaResultado")
            rows = await page.locator("#tabelaResultado tbody tr").all()
            data = [await _extract_row(row) for row in rows]
            headers = ['ticker', 'segmento', 'cotação', 'ffo yield', 'dividend yield', 'p/vp', 'valor de mercado',
                       'liquidez', 'qtd de imóveis', 'preço do m2', 'aluguel por m2', 'cap rate', 'vacância média']
            df = pandas.DataFrame(data, columns=headers)
            df.to_csv(path, index=False)
    except Exception as e:
        log(error_name(e), '_global', name)


async def _extract_row(row):
    cells = await row.locator("td").all_text_contents()
    if cells:
        return [c.replace("%", "").replace(".", "").replace(",", ".").strip() for c in cells[:-1]]
    else:
        return None
