import os, re, glob


def move_file(src_path, dst_path):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    os.rename(src_path, dst_path)


def get_all_files(dir_path: str, filter_term: str):
    return [path for path in glob.glob(f"{dir_path}/*") if filter_term in path]


def get_ticker(path: str):
    return re.match(r'.*/\w+?-(\w+)+.*', path).group(1)
