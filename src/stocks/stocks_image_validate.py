import os, easyocr, warnings

warnings.filterwarnings("ignore", message=".*pin_memory.*MPS.*")
reader = easyocr.Reader(['en'])

def validate(path):
    if os.path.exists(path):
        lines = reader.readtext(path, detail=0)
        is_error = any(line.find('error') > 0 for line in lines)
        is_short = len(lines) < 50
        return not is_error or not is_short
    else:
        return False