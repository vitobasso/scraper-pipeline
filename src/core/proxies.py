import glob
from src.core.config import config
import random

input_dir = config.get('proxies.lists_dir')

def random_proxy():
    return random.choice(proxies)

def _load_all_lists():
    return [
        line
        for file in glob.glob(f"{input_dir}/*")
        for line in _load_list(file)
    ]

def _load_list(file: str):
    with open(file) as f:
        return f.read().splitlines()

proxies = _load_all_lists()