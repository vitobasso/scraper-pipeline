import easyocr, warnings

_reader = None


def ocr():
    if not _reader:
        _init()
    return _reader


def _init():
    warnings.filterwarnings("ignore", message=".*pin_memory.*MPS.*")
    global _reader
    _reader = easyocr.Reader(['en'])
