import os, json, re
from pathlib import Path
from typing import Callable
from src.common.util import mkdir

input_dir = lambda x: mkdir(f'{x}/data/awaiting-validation')
valid_data_dir = lambda x: mkdir(f'{x}/data/ready')
invalid_data_dir = lambda x: mkdir(f'{x}/data/failed-validation')
failed_data_dir = lambda x: mkdir(f'{x}/data/failed-extraction')


def validate_schema(path: str, schema, output_dir: str):
    validator = lambda data: _validate_dict(data, schema)
    validate_json(path, validator, output_dir)


def validate_json(path: str, validator: Callable[[str], list], output_dir: str):
    if _is_extraction_error(path):
        failed_path = f'{failed_data_dir(output_dir)}/{os.path.basename(path)}'
        os.rename(path, failed_path)
    else:
        errors = _validate_json(path, validator)
        dest_dir = invalid_data_dir(output_dir) if errors else valid_data_dir(output_dir)
        dest_path = f'{dest_dir}/{Path(path).name}'
        os.rename(path, dest_path)
        if errors:
            _append_errors(dest_path, errors)


def _is_extraction_error(path):
    with open(path) as f:
        first_line = f.readline()
        return re.search(r'^\w', first_line) and not re.search(r'[{}]', first_line)


def _validate_json(path: str, validator: Callable[[str], list]):
    try:
        with open(path) as f:
            return validator(json.load(f))
    except Exception as e:
        return [str(e)]


def _validate_dict(data, schema, path=''):
    return [error
            for key, rule in schema.items()
            for error in _validate_field(data, key, rule, path)]


def _validate_field(data, key, rule, parent_path):
    path = f"{parent_path}.{key}" if parent_path else key
    expected, optional = (rule[0], True) if isinstance(rule, tuple) else (rule, False)
    if key in data:
        return _validate_type(data[key], expected, path)
    elif not optional:
        return [f"{path}: missing"]
    return []


def _validate_type(actual, expected, path):
    if isinstance(expected, dict):
        return _validate_dict(actual, expected, path) if isinstance(actual, dict) \
            else [_invalid_type(actual, dict, path)]
    else:
        return [] if isinstance(actual, expected) else [_invalid_type(actual, expected, path)]


def _invalid_type(actual, expected, path):
    actual_type = 'null' if actual is None else type(actual).__name__
    return f"{path}: expected {expected.__name__}, got {actual_type}"


def _append_errors(path, errors):
    with open(path, "a") as f:
        f.write('\n\n')
        f.writelines([e + "\n" for e in errors])
