import asyncio
import csv
import re
from itertools import chain
from pathlib import Path

from src.common.services.data import known_tickers
from src.scraper.core.logs import log
from src.scraper.core.paths import for_pipe
from src.scraper.core.scheduler import Pipeline
from src.scraper.core.tasks import normalization
from src.scraper.core.tasks.base import global_task, intermediate_task
from src.scraper.core.util import xls, zip
from src.scraper.services.browser import download_bytes, error_name, find_url_contains, page_goto
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
    out_csv = for_pipe(pipe, "_global").output_file("normalization", "csv")
    proxy = random_proxy(pipe)
    url = "https://sistemaswebb3-listados.b3.com.br/listedCompaniesPage/"
    print(f"downloading csv, url: {url}, path: {out_csv}, proxy: {proxy}")
    try:
        async with page_goto(proxy, url) as page:
            zip_url = await find_url_contains(page, url, ".zip")
            zip_bytes = await download_bytes(page, zip_url)
            _, xlsx_bytes = zip.first_file(zip_bytes, selector=".xlsx")
            xls.to_csv(xlsx_bytes, out_csv)
    except Exception as e:
        log(error_name(e), "_global", pipe)


def normalize(pipe: Pipeline, input_csv: Path):
    print(f"normalizing, path: {input_csv}")
    try:
        _normalize(pipe, input_csv)
        normalization.stamp_ready(input_csv)
    except Exception as e:
        log(str(e), "_global", pipe)


def _normalize(pipe: Pipeline, input_csv: Path):
    # Read from CSV generated in download stage
    with input_csv.open(encoding="utf-8") as f:
        reader = csv.reader(f)

        buffered = _probe_buffer(reader)
        header_idx = _find_header_index(buffered)
        headers_found = _coalesce_headers(buffered, header_idx, depth=3)

        col_index = {h: i for i, h in enumerate(headers_found)}
        ticker_col = col_index.get("codigo")
        if ticker_col is None:
            raise ValueError("'codigo' column not found in headers")

        headers_desired = ("setor", "subsetor", "segmento", "segmento_de_negociacao")
        last_seen: dict[str, str | None] = {k: None for k in headers_desired}

        def process_row(row: list[str]):
            # map row -> data with cleaning and forward-fill
            cleaned_values = [_clean(v) for v in row]
            data = {headers_found[i]: cleaned_values[i] for i in range(min(len(headers_found), len(cleaned_values)))}
            for key in last_seen.keys():
                val = data.get(key)
                if val is None and last_seen[key] is not None:
                    data[key] = last_seen[key]  # propagate last seen when empty
                elif val is not None:
                    # only update last_seen when we got a concrete value
                    last_seen[key] = val
            # discard extra cols
            data = {k: v for k, v in data.items() if k in headers_desired}
            return data

        valid_tickers = known_tickers(pipe.asset_class)

        # Single pass over rows after header (buffer tail + remaining reader)
        for row in chain(buffered[header_idx + 1 :], reader):
            # update state (last_seen) even when we won't emit a record
            data = process_row(row)
            if len(row) <= ticker_col:
                continue
            ticker_prefix = row[ticker_col].upper()
            if not ticker_prefix:
                continue
            tickers = find_tickers(ticker_prefix, valid_tickers)
            if not tickers:
                continue
            for t in tickers:
                normalization.write_output(data, pipe, t, input_csv)


def find_tickers(partial, valid_tickers):
    partial = partial.upper()
    pattern = re.compile(rf"^{re.escape(partial)}\d{{1,2}}$")
    return [t for t in valid_tickers if pattern.match(t)]


def _probe_buffer(reader, max_probe: int = 10) -> list[list[str]]:
    buffered: list[list[str]] = []
    for _ in range(max_probe):
        try:
            row = next(reader)
            buffered.append(row)
        except StopIteration:
            break
    return buffered


def _find_header_index(buffered: list[list[str]]) -> int:
    expected = {
        "setor",
        "subsetor",
        "segmento",
        "emissor",
        "nome_de_pregao",
        "codigo",
        "segmento_de_negociacao",
    }
    header_idx = 0
    best_score = -1
    for i, r in enumerate(buffered):
        norm = [normalization.key(c or "") for c in r]
        score = sum(1 for c in norm if c in expected)
        if score > best_score:
            best_score = score
            header_idx = i
    return header_idx


def _coalesce_headers(buffered: list[list[str]], header_idx: int, depth: int = 3) -> list[str]:
    # Coalesce non-empty cells from header row and a few rows below into a single header list
    lines = buffered[header_idx : header_idx + depth]
    max_len = max((len(r) for r in lines), default=0)
    out: list[str] = []
    for j in range(max_len):
        cell = None
        for i in range(len(lines)):
            try:
                v = lines[i][j]
            except IndexError:
                v = None
            v = _clean(v)
            if v:
                cell = v
                break
        out.append(normalization.key(cell or ""))
    return out


def _clean(v):
    try:
        v = v.strip()
        # treat common placeholders as empty to enable forward-fill
        placeholders = {"", "-", "–", "—", "N/A", "n/a", "NA", "na"}
        return None if v in placeholders else v
    except AttributeError:
        return v
