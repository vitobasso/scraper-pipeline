import sqlite3
from pathlib import Path

from cachetools.func import ttl_cache

from src.config import output_root
from src.core.util import mkdir

db_file = mkdir(Path(output_root)) / "db.sqlite"


def run_script(filename):
    with open(filename, "r") as f:
        sql = f.read()
        with sqlite3.connect(db_file) as conn:
            cur = conn.cursor()
            cur.executescript(sql)


@ttl_cache(ttl=10)
def query_all_tickers(limit=20, offset=0):
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        query = """
                SELECT s.ticker
                FROM tickers s
                ORDER BY s.last_requested DESC LIMIT :limit
                OFFSET :offset;
                """
        params = {
            "limit": limit,
            "offset": offset,
        }
        cur.execute(query, params)
        tickers = [row[0] for row in cur.fetchall()]
        return tickers
