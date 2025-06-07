import os, json, re
from src.config import output_dir
from src.core.util import mkdir

data_dir = f'{output_dir}/data'
valid_data_dir = mkdir(f'{data_dir}/ready')
invalid_data_dir = mkdir(f'{data_dir}/failed-validation')
failed_data_dir = mkdir(f'{data_dir}/failed-extraction')


def validate(path: str, schema):
    if _is_extraction_error(path):
        failed_path = f'{failed_data_dir}/{os.path.basename(path)}'
        os.rename(path, failed_path)
    else:
        errors = _validate_json(path, schema)
        dest_dir = invalid_data_dir if errors else valid_data_dir
        dest_path = f'{dest_dir}/{os.path.basename(path)}'
        os.rename(path, dest_path)
        if errors:
            _append_errors(dest_path, errors)


def _is_extraction_error(path):
    with open(path) as f:
        first_line = f.readline()
        return re.search(r'^\w', first_line) and not re.search(r'[{}]', first_line)


def _validate_json(path: str, schema):
    try:
        with open(path) as f:
            return _validate_dict(json.load(f), schema)
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
