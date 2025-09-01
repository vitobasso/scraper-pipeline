from pathlib import Path

from src.common import config
from src.common.services import repository


def known_tickers(asset_class: str, limit: int = 1000) -> list[str]:
    """
    Merge tickers from:
      1) repository.query_tickers
      2) first-level directories under data_root (excluding names starting with '_')

    Returns a sorted list of unique tickers (uppercased).
    """
    # 1) DB
    repo = {t.upper() for t in (repository.query_tickers(asset_class, limit=limit) or [])}

    # 2) Filesystem
    root = Path(config.data_root) / asset_class
    if root.exists():
        fs = {p.name.upper() for p in root.iterdir() if p.is_dir() and not p.name.startswith("_")}
    else:
        fs = set()

    return sorted(repo | fs)
