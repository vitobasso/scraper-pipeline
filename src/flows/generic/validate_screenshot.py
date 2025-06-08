import os, easyocr, warnings
from pathlib import Path
from src.core.util import mkdir

ocr_min_lines = 50

input_dir = lambda x: mkdir(f'{x}/screenshots/awaiting-validation')
valid_dir = lambda x: mkdir(f'{x}/screenshots/awaiting-extraction')
invalid_dir = lambda x: mkdir(f'{x}/screenshots/failed-validation')
warnings.filterwarnings("ignore", message=".*pin_memory.*MPS.*")
reader = easyocr.Reader(['en'])


def validate_screenshot(image_path: str, output_dir: str):
    dest_dir = valid_dir(output_dir) if _validate(image_path) else invalid_dir(output_dir)
    dest_path = f'{dest_dir}/{Path(image_path).name}'
    os.rename(image_path, dest_path)


def _validate(image_path: str):
    lines = reader.readtext(image_path, detail=0)
    is_error = any(line.find('error') > 0 for line in lines)
    is_short = len(lines) < ocr_min_lines
    return not is_error or not is_short
