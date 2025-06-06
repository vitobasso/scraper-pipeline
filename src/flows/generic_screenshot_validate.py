import os, easyocr, warnings
from src.core.config import config

screenshot_dir = 'output/screenshots'
ocr_min_lines = config.get('screenshot.validator.ocr.min_lines')
warnings.filterwarnings("ignore", message=".*pin_memory.*MPS.*")
reader = easyocr.Reader(['en'])

def validate(image_path: str):
    filename = os.path.basename(image_path)
    valid_path = f'{screenshot_dir}/awaiting-extraction/{filename}'
    invalid_path = f'{screenshot_dir}/failed-validation/{filename}'
    dest_path = valid_path if _validate(image_path) else invalid_path
    _move_file(image_path, dest_path)

def _validate(image_path: str):
    lines = reader.readtext(image_path, detail=0)
    is_error = any(line.find('error') > 0 for line in lines)
    is_short = len(lines) < ocr_min_lines
    return not is_error or not is_short

def _move_file(src_path, dst_path):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    os.rename(src_path, dst_path)
