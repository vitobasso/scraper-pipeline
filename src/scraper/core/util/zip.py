import re
import zipfile
from collections.abc import Callable
from io import BytesIO
from re import Pattern


def first_file(
    zip_bytes: bytes,
    selector: str | Pattern[str] | Callable[[str], bool] | None = None,
) -> tuple[str, bytes]:
    """Return the first file from a ZIP matching the given selector.

    - selector is None: return the first file (archive order).
    - selector is str: case-insensitive substring match ("contains").
    - selector is re.Pattern: regex search on filename.
    - selector is callable: predicate receiving the filename -> bool.

    Returns (filename, bytes).
    Raises ValueError if no files match or zip is empty.
    """

    def matches(name: str) -> bool:
        if selector is None:
            return True
        if callable(selector):
            try:
                return bool(selector(name))
            except Exception:
                return False
        if isinstance(selector, re.Pattern):
            return bool(selector.search(name))
        if isinstance(selector, str):
            return selector.lower() in name.lower()
        # Unknown selector type: no match
        return False

    with zipfile.ZipFile(BytesIO(zip_bytes), "r") as zf:
        names = zf.namelist()
        if not names:
            raise ValueError("ZIP is empty")

        for name in names:
            if matches(name):
                return name, zf.read(name)

        raise ValueError(f"No file in ZIP matched the selector: {selector}")
