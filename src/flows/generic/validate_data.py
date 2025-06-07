import os, json
from src.config import output_dir
from src.core.util import mkdir

data_dir = f'{output_dir}/data'
valid_data_dir = mkdir(f'{data_dir}/ready')
invalid_data_dir = mkdir(f'{data_dir}/failed-validation')


def validate_json(path: str, validate_dict):
    dest_dir = valid_data_dir if _validate_json(path, validate_dict) else invalid_data_dir
    dest_path = f'{dest_dir}/{os.path.basename(path)}'
    os.rename(path, dest_path)


def _validate_json(path: str, validate_dict):
    try:
        with open(path) as f:
            dict = json.load(f)
        return validate_dict(dict)
    except:
        return False


# TODO instead of validate_dict, pass just a dict with required keys (with None as values)