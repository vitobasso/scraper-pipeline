from tinydb import TinyDB, Query
import datetime
from random import randrange, choice

with open("resources/proxies.txt") as f:
    proxies = f.read().splitlines()

db = TinyDB('proxies.json')

for line in proxies:
    db.upsert({'proxy': line}, Query().proxy == line)
    
def report(proxy: str, succeeded: bool):
    if records := db.search(Query().proxy == proxy):
        record = records[0]
        record["count_usages"] = record.get("count_usages", 0) + 1
        record["last_used"] = datetime.datetime.now().timestamp()
        if succeeded:
            record["count_successes"] = record.get("count_successes", 0) + 1
            record["last_succeeded"] = record["last_used"]
        db.update(record, Query().proxy == proxy)

def pick():
    record = _pick()
    return record["proxy"] if record else None

def _pick():
    all_proxies = db.all()
    healthy = [x for x in all_proxies if _is_healthy(x)]
    never_used = [x for x in all_proxies if _is_never_used(x)]
    retriable = [x for x in all_proxies if _is_retriable(x)]
    if randrange(0, 10) < 9:
        return _pick_random(never_used) or _pick_oldest(retriable) or _pick_oldest(healthy)
    else:
        return _pick_oldest(healthy) or _pick_random(never_used) or _pick_oldest(retriable)

def _pick_oldest(_list):
    return sorted(_list, key=lambda x: x["last_used"], reverse=True)[0] if _list else None

def _pick_random(_list):
    return choice(_list) if _list else None

def _is_never_used(record):
    return record.get("last_used") is None

def _is_healthy(record):
    day_secs = 60 * 60 * 24
    return not _is_never_used(record) and record.get("last_used") - record.get("last_succeeded", 0) < day_secs

def _is_retriable(record):
    if _is_never_used(record) or _is_healthy(record):
        return False
    else:
        count_failures = record.get("count_usages", 0) - record.get("count_successes", 0)
        ratio_success = record.get("count_successes", 0) / record.get("count_usages", 0)
        return count_failures < 10 or ratio_success > .1
