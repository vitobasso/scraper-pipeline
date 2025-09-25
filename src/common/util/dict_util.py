from typing import Any


def flatten(d, depth=0, parent_key="") -> dict[str, Any]:
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict) and depth:
            items.update(flatten(v, depth - 1, new_key))
        else:
            items[new_key] = v
    return items
