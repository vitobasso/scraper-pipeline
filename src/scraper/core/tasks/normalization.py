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
from src.scraper.core.scheduler import Pipeline, TaskFactory
from src.scraper.core.tasks.base import intermediate_task
from src.scraper.core.util.files import iterate_csv, write_json


def normalize_json(function: Callable[[dict], dict], next_stage: str = "ready") -> TaskFactory:
    execute = lambda pipe, path: _normalize_json(path, function, next_stage)
    return intermediate_task(execute, "normalization")


def normalize_json_split(function: Callable[[dict], list[tuple[str, dict]]], output_to_pipe: str = None) -> TaskFactory:
    """
    Splits the input json into one output json per ticker.
    """
    execute = lambda pipe, path: _normalize_json_split(path, function, output_to_pipe)
    return intermediate_task(execute, "normalization")


def normalize_csv(function: Callable[[dict], dict], delimiter: str = ",") -> TaskFactory:
    """
    Splits the csv into one json per ticker.
    """
    execute = lambda pipe, path: _normalize_csv_split(path, function, delimiter)
    return intermediate_task(execute, "normalization")


def _normalize_json(input_path: Path, function: Callable[[dict], dict], next_stage: str = "ready"):
    print(f"normalizing, path: {input_path}")
    try:
        with input_path.open(encoding="utf-8") as f:
            data = function(json.load(f))
        output, _, processed = paths.split_files(input_path, "normalization", next_stage)
        write_json(data, output)
        input_path.rename(processed)
    except Exception as e:
        log_for_path(str(e), input_path)


def _normalize_json_split(input_path: Path, function: Callable[[dict], list[tuple[str, dict]]], alt_pipe: str = None):
    print(f"normalizing, path: {input_path}")
    try:
        asset_class, _, pipe_name = paths.parts(input_path)
        with input_path.open(encoding="utf-8") as f:
            for ticker, data in function(json.load(f)):
                _write_output(data, asset_class, ticker, alt_pipe or pipe_name, input_path)
        stamp_ready(input_path)
    except Exception as e:
        log_for_path(str(e), input_path)


def _normalize_csv_split(input_path: Path, function: Callable[[dict], dict], delimiter: str = ","):
    print(f"normalizing, path: {input_path}")
    try:
        asset_class, _, pipe_name = paths.parts(input_path)
        requested_tickers = set(repository.query_tickers(asset_class))
        for ticker, data_raw in iterate_csv(input_path, delimiter):
            if config.only_requested_tickers and ticker not in requested_tickers:
                continue
            data_norm = function(data_raw)
            _write_output(data_norm, asset_class, ticker, pipe_name, input_path)

        stamp_ready(input_path)
    except Exception as e:
        log_for_path(str(e), input_path)


def write_output(data: dict, pipe: Pipeline, ticker: str, input_path: Path):
    _write_output(data, pipe.asset_class, ticker, pipe.name, input_path)


def _write_output(data: dict, asset_class: str, ticker: str, pipe_name: str, input_path: Path):
    out_path = paths.for_parts(asset_class, ticker, pipe_name).stage_dir("ready") / f"{input_path.stem}.json"
    write_json(data, out_path)


def stamp_ready(input_path):
    output, _, processed = paths.split_files(input_path, "normalization", "ready", "stamp")
    input_path.rename(processed)
    if not paths.for_child(input_path).has_waiting_files:
        # Signal to Progress that this "global" task is complete
        # The actual output data was split to folders per ticker
        output.touch()


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
