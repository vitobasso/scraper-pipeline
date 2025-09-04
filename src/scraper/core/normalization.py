import csv
import json
import re
import unicodedata
from collections.abc import Callable
from functools import reduce
from pathlib import Path

from src.common import config
from src.common.services import repository
from src.scraper.core import paths
from src.scraper.core.logs import log_for_path


def normalize_json(input_path: Path, function: Callable, next_stage: str = "ready"):
    print(f"normalizing, path: {input_path}")
    try:
        with input_path.open(encoding="utf-8") as f:
            data = function(json.load(f))
        output, _, processed = paths.split_files(input_path, "normalization", next_stage)
        with output.open(mode="w", encoding="utf-8") as f:
            json.dump(data, f)
        input_path.rename(processed)
    except Exception as e:
        log_for_path(str(e), input_path)


def normalize_csv(input_path: Path, function: Callable, next_stage: str, delimiter: str = ","):
    print(f"normalizing, path: {input_path}")
    try:
        _normalize_csv(input_path, function, delimiter)
        output, _, processed = paths.split_files(input_path, "normalization", next_stage, "stamp")
        input_path.rename(processed)
        output.touch()
    except Exception as e:
        log_for_path(str(e), input_path)


def _normalize_csv(input_path: Path, function: Callable, delimiter: str = ","):
    """
    Splits the csv into one json per ticker.
    Assumptions:
     - csv contains multiple tickers
     - the first line is the header
     - the first column contains tickers
    """
    asset_class, _, pipe_name = paths.parts(input_path)
    requested_tickers = set(repository.query_tickers(asset_class))
    with input_path.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        headers = [h for h in (next(reader))]

        for row in reader:
            if not row:
                continue
            ticker, *rest = row
            if config.only_requested_tickers and ticker not in requested_tickers:
                continue
            values = [v for v in rest]
            data_raw = dict(zip(headers, [ticker] + values, strict=False))
            data_norm = function(data_raw)

            out_path = paths.for_parts(asset_class, ticker, pipe_name).stage_dir("ready") / f"{input_path.stem}.json"
            with out_path.open("w", encoding="utf-8") as out:
                json.dump(data_norm, out, ensure_ascii=False, indent=2)


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
    except (ValueError, TypeError, AttributeError):
        return v


def key(k: str) -> str:
    k = k.lower()
    # remove accents
    k = "".join(c for c in unicodedata.normalize("NFKD", k) if not unicodedata.combining(c))
    # replace symbols with space
    k = re.sub(r"[^a-z0-9]+", " ", k)
    # trim and replace spaces with underscores
    return "_".join(k.strip().split())


def remove_keys(*keys: str):
    return lambda d: _remove_keys(d, *keys)


def _remove_keys(data, *keys: str):
    for k in keys:
        data.pop(k, None)
    return data


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
