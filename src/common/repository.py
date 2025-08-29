import sqlite3
from datetime import datetime
from pathlib import Path

from cachetools.func import ttl_cache

from src.common.config import data_root
from src.common.util import mkdir

db_file = mkdir(Path(data_root)) / "db.sqlite"


def run_script(filename: str):
    with open(filename) as f:
        sql = f.read()
        with sqlite3.connect(db_file) as conn:
            cur = conn.cursor()
            cur.executescript(sql)


@ttl_cache(ttl=10)
def query_tickers(limit: int = 20, offset: int = 0):
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        query = """
                SELECT s.ticker
                FROM tickers s
                ORDER BY s.last_requested DESC
                LIMIT :limit OFFSET :offset;
                """
        params = {
            "limit": limit,
            "offset": offset,
        }
        cur.execute(query, params)
        tickers = [row[0] for row in cur.fetchall()]
        return tickers


def upsert_tickers(tickers: list[str]):
    last_requested = datetime.now()
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute("BEGIN")
        for ticker in tickers:
            query = """
                    INSERT OR REPLACE INTO tickers (ticker, last_requested)
                    VALUES (:ticker, :last_requested)
                    """
            params = {
                "ticker": ticker,
                "last_requested": last_requested.replace(microsecond=0),
            }
            cur.execute(query, params)
        cur.execute("COMMIT")
