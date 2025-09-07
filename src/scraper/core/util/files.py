import csv
import json
from collections.abc import Iterable
from pathlib import Path


def mkdir(path: Path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def last_file(dir_path: Path) -> Path | None:
    if not dir_path.exists():
        return None
    files = list(dir_path.glob("*"))
    return max(files) if files else None


def read_lines(input_path: Path) -> list[str]:
    with input_path.open(encoding="utf-8") as f:
        return [line.strip() for line in f]


def write_lines(lines: list[str], out_path: Path):
    with out_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_json(data: dict, out_path: Path):
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f)


def iterate_csv(input_path: Path, delimiter: str = ",") -> Iterable[tuple[str, dict]]:
    """
    Assumes:
     - csv contains multiple tickers
     - the first line is the header
     - the first column contains tickers
    """
    with input_path.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        headers = [h for h in (next(reader))]
        for row in reader:
            if not row:
                continue
            ticker, *rest = row
            values = [v for v in rest]
            yield ticker, dict(zip(headers, [ticker] + values, strict=False))
