import os, easyocr, warnings
from src.core.config import config

ocr_min_lines = config.get('screenshot.validator.ocr.min_lines')
warnings.filterwarnings("ignore", message=".*pin_memory.*MPS.*")
reader = easyocr.Reader(['en'])

def validate(path: str):
    if os.path.exists(path):
        lines = reader.readtext(path, detail=0)
        is_error = any(line.find('error') > 0 for line in lines)
        is_short = len(lines) < ocr_min_lines
        return not is_error or not is_short
    else:
        return False