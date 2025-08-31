import json
import re
import unicodedata
from collections.abc import Callable
from pathlib import Path
from functools import reduce

from src.scraper.core import paths
from src.scraper.core.logs import log


def normalize_json(input_path: Path, function: Callable, next_stage: str):
    print(f"normalizing, path: {input_path}")
    try:
        with input_path.open(encoding="utf-8") as f:
            data = function(json.load(f))
        output, _, processed = paths.split_files(input_path, "normalization", next_stage)
        with output.open(mode="w", encoding="utf-8") as f:
            json.dump(data, f)
        input_path.rename(processed)
    except Exception as e:
        ticker, pipeline = paths.extract_ticker_pipeline(input_path)
        log(str(e), ticker, pipeline)


def pipe(*funcs: Callable):
    return lambda v: reduce(lambda acc, f: f(acc), funcs, v)


def rename_keys(rename_dict):
    return traverse_keys(lambda k: rename_dict.get(k, k))


def value(v):
    v = string(v)
    return number(v)


def string(v):
    try:
        v = v.strip()
        return None if v == "" else v
    except AttributeError:
        return v


def number(v):
    try:
        replaced = v.replace("R$", "").replace("%", "").replace(".", "").replace(",", ".").strip()
        return float(replaced)
    except (ValueError, TypeError):
        return v


def key(header: str) -> str:
    header = header.lower()
    # remove accents
    header = "".join(c for c in unicodedata.normalize("NFKD", header) if not unicodedata.combining(c))
    # replace symbols with space
    header = re.sub(r"[^a-z0-9]+", " ", header)
    # trim and replace spaces with underscores
    return "_".join(header.strip().split())


def traverse_keys(func):
    return lambda d: _traverse_keys(d, func)


def _traverse_keys(d, func):
    if isinstance(d, dict):
        return {func(k): _traverse_keys(v, func) for k, v in d.items()}
    elif isinstance(d, list):
        return [_traverse_keys(x, func) for x in d]
    else:
        return d


def traverse_values(func):
    return lambda d: _traverse_values(d, func)


def _traverse_values(d, func):
    if isinstance(d, dict):
        return {k: _traverse_values(v, func) for k, v in d.items()}
    elif isinstance(d, list):
        return [_traverse_values(v, func) for v in d]
    else:
        return func(d)


def traverse_dict(transform_dict: dict[str, Callable]):
    return lambda d: _traverse_dict(d, transform_dict)


def _traverse_dict(d, func_dict: dict[str, Callable]):
    if isinstance(d, dict):
        out = {}
        for k, v in d.items():
            if k in func_dict:
                try:
                    out[k] = func_dict[k](v)
                except Exception:
                    out[k] = v
            else:
                out[k] = _traverse_dict(v, func_dict)
        return out
    elif isinstance(d, list):
        return [_traverse_dict(x, func_dict) for x in d]
    else:
        return d
