import os, re, glob


def mkdir(path):
    os.makedirs(path, exist_ok=True)
    return path


def all_files(dir_path: str):
    return glob.glob(f"{dir_path}/**/*")


def get_ticker(path: str):
    return re.match(r'.*/\w+?-(\w+)+.*', path).group(1)
