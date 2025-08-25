import json
from collections.abc import Callable
from pathlib import Path

from src.core import paths
from src.core.logs import log


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


def rename_keys(rename_dict):
    def func(data):
        if isinstance(data, dict):
            return {rename_dict.get(k, k): func(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [func(x) for x in data]
        else:
            return data

    return func
