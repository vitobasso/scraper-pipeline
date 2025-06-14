import asyncio, sys, pandas
from src.common.util import timestamp, mkdir
from src.config import output_root
from src.scheduler import Pipeline, seed_task, seed_progress
from src.services.browser import page_goto, error_name
from src.services.proxies import random_proxy

name = 'fundamentus_fiis'
output_dir = mkdir(f'{output_root}/{name}')


def pipeline() -> Pipeline:
    return {
        'name': name,
        'tasks': [
            seed_task(scrape, output_dir),
        ],
        'progress': seed_progress(output_dir)
    }


def scrape():
    url = 'https://www.fundamentus.com.br/fii_resultado.php'
    path = f'{output_dir}/{timestamp()}.csv'
    proxy = random_proxy()
    asyncio.run(_scrape(proxy, url, path))


async def _scrape(proxy: str, url: str, path: str):
    print(f'scraping html, url: {url}, path: {path}, proxy: {proxy}')
    try:
        async with page_goto(proxy, url, wait_until='domcontentloaded') as page:
            await page.wait_for_selector("#tabelaResultado")
            rows = await page.locator("#tabelaResultado tbody tr").all()
            data = [await _extract_row(row) for row in rows]
            headers = ['ticker', 'segmento', 'cotação', 'ffo yield', 'dividend yield', 'p/vp', 'valor de mercado',
                          'liquidez', 'qtd de imóveis', 'preço do m2', 'aluguel por m2', 'cap rate', 'vacância média']
            df = pandas.DataFrame(data, columns = headers)
            df.to_csv(path, index=False)
    except Exception as e:
        print(f'failed: {error_name(e)}', file=sys.stderr)


async def _extract_row(row):
    cells = await row.locator("td").all_text_contents()
    if cells:
        return [c.replace("%", "").replace(".", "").replace(",", ".").strip() for c in cells[:-1]]
    else:
        return None
