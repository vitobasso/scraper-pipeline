from pathlib import Path


def mkdir(path: Path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def last_file(dir_path: Path) -> Path | None:
    if not dir_path.exists():
        return None
    files = list(dir_path.glob("*"))
    return max(files) if files else None
