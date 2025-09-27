import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from cachetools.func import ttl_cache

from src.common import config
from src.scraper.core.util.files import mkdir

db_file = mkdir(Path(config.data_root)) / "db.sqlite"


def init():
    if not db_file.exists():
        build_db()


@ttl_cache(ttl=10)
def query_tickers(asset_class: str, limit: int = 100, offset: int = 0) -> list[str]:
    init()
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        query = """
                SELECT s.ticker
                FROM tickers s
                WHERE s.asset_class = :asset_class
                ORDER BY s.last_requested DESC
                LIMIT :limit OFFSET :offset;
                """
        params = {
            "asset_class": asset_class,
            "limit": limit,
            "offset": offset,
        }
        cur.execute(query, params)
        tickers = [row[0] for row in cur.fetchall()]
        return tickers


def upsert_tickers(tickers: list[str], asset_class: str):
    init()
    last_requested = datetime.now()
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute("BEGIN")
        for ticker in tickers:
            query = """
                    INSERT OR REPLACE INTO tickers (ticker, asset_class, last_requested)
                    VALUES (:ticker, :asset_class, :last_requested)
                    """
            params = {
                "ticker": ticker,
                "asset_class": asset_class,
                "last_requested": last_requested.replace(microsecond=0),
            }
            cur.execute(query, params)
        cur.execute("COMMIT")


def query_scrapes_since(date_since: datetime, tickers: list[str]) -> set[tuple[str, str, str]]:
    init()
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        _tickers = ["_global", *tickers]
        placeholders = ",".join("?" for _ in _tickers)
        query = f"""
                SELECT asset_class, ticker, pipeline
                FROM scrapes
                WHERE ticker IN ({placeholders})
                AND last_scraped > ?
                """
        params = [*_tickers, date_since.replace(microsecond=0).isoformat(sep=" ")]
        cur.execute(query, params)
        out = set()
        for asset_class, ticker, pipeline in cur.fetchall():
            out.add((asset_class, ticker, pipeline))
        return out


def upsert_scrape(asset_class: str, ticker: str, pipeline: str):
    init()
    last_scraped = datetime.now(UTC)
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        query = """
                INSERT OR REPLACE INTO scrapes (ticker, asset_class, pipeline, last_scraped)
                VALUES (:ticker, :asset_class, :pipeline, :last_scraped)
                """
        params = {
            "ticker": ticker,
            "asset_class": asset_class,
            "pipeline": pipeline,
            "last_scraped": last_scraped.replace(microsecond=0),
        }
        cur.execute(query, params)


def run_script(filename: str):
    with open(filename) as f:
        sql = f.read()
        with sqlite3.connect(db_file) as conn:
            cur = conn.cursor()
            cur.executescript(sql)


def build_db():
    run_script("resources/sql-schema/schema.sql")
    run_script("resources/sql-schema/seed_data.sql")
    # run_script("resources/sql-schema/migrate.sql")
