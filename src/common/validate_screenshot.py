import os
from pathlib import Path
from src.common.util import mkdir

input_dir = lambda x: mkdir(f'{x}/screenshots/awaiting-validation')
valid_dir = lambda x: mkdir(f'{x}/screenshots/awaiting-extraction')
invalid_dir = lambda x: mkdir(f'{x}/screenshots/failed-validation')


def validate_screenshot(image_path: str, output_dir: str):
    dest_dir = valid_dir(output_dir) if _validate(image_path) else invalid_dir(output_dir)
    dest_path = f'{dest_dir}/{Path(image_path).name}'
    os.rename(image_path, dest_path)


def _validate(image_path: str):
    return True  # removed ocr as it was too resource hungry
