import os, easyocr, warnings
from src.config import output_dir
from src.core.util import mkdir

ocr_min_lines = 50

input_dir = mkdir(f'{output_dir}/screenshots/awaiting-validation')
valid_dir = mkdir(f'{output_dir}/screenshots/awaiting-extraction')
invalid_dir = mkdir(f'{output_dir}/screenshots/failed-validation')
warnings.filterwarnings("ignore", message=".*pin_memory.*MPS.*")
reader = easyocr.Reader(['en'])


def validate(image_path: str):
    dest_dir = valid_dir if _validate(image_path) else invalid_dir
    dest_path = f'{dest_dir}/{os.path.basename(image_path)}'
    os.rename(image_path, dest_path)


def _validate(image_path: str):
    lines = reader.readtext(image_path, detail=0)
    is_error = any(line.find('error') > 0 for line in lines)
    is_short = len(lines) < ocr_min_lines
    return not is_error or not is_short
