from pathlib import Path

from src.common import config, repository


def known_tickers(limit: int = 1000) -> list[str]:
    """
    Merge tickers from:
      1) repository.query_tickers
      2) first-level directories under data_root (excluding names starting with '_')

    Returns a sorted list of unique tickers (uppercased).
    """
    # 1) DB
    repo = {t.upper() for t in (repository.query_tickers(limit=limit) or [])}

    # 2) Filesystem
    root = Path(config.data_root)
    if root.exists():
        fs = {p.name.upper() for p in root.iterdir() if p.is_dir() and not p.name.startswith("_")}
    else:
        fs = set()

    return sorted(repo | fs)
