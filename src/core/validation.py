import json
import re
from pathlib import Path
from typing import Callable

from src.core import paths


def validate_schema(path: Path, schema: dict, next_stage: str):
    validator = lambda data: _validate_dict(data, schema)
    validate_json(path, validator, next_stage)


def validate_json(path: Path, validator: Callable[[str], list], next_stage: str):
    if _is_extraction_error(path):
        _, failed, _ = paths.split_files(path, "extraction", next_stage)
        path.rename(failed)
    else:
        errors = _validate_json(path, validator)
        output, failed, _ = paths.split_files(path, "validation", next_stage)
        dest_path = failed if errors else output
        path.rename(dest_path)
        if errors:
            _append_errors(dest_path, errors)


def _is_extraction_error(path: Path):
    with open(path) as f:
        first_line = f.readline()
        return re.search(r'^\w', first_line) and not re.search(r'[{}]', first_line)


def _validate_json(path: Path, validator: Callable[[str], list]):
    try:
        with open(path) as f:
            return validator(json.load(f))
    except Exception as e:
        return [str(e)]


def _validate_dict(data, schema, path: str = '') -> list:
    return [error
            for key, rule in schema.items()
            for error in _validate_field(data, key, rule, path)]


def _validate_field(data, key: str, rule, parent_path: str) -> list:
    path = f"{parent_path}.{key}" if parent_path else key
    expected, optional = (rule[0], True) if isinstance(rule, tuple) else (rule, False)
    if key in data:
        return _validate_type(data[key], expected, path)
    elif not optional:
        return [f"{path}: missing"]
    return []


def _validate_type(actual, expected, path: str):
    if isinstance(expected, dict):
        return _validate_dict(actual, expected, path) if isinstance(actual, dict) \
            else [_invalid_type(actual, dict, path)]
    else:
        return [] if isinstance(actual, expected) else [_invalid_type(actual, expected, path)]


def _invalid_type(actual, expected, path: str):
    actual_type = 'null' if actual is None else type(actual).__name__
    return f"{path}: expected {expected.__name__}, got {actual_type}"


def _append_errors(path: Path, errors):
    with open(path, "a") as f:
        f.write('\n\n')
        f.writelines([e + "\n" for e in errors])
