import datetime
from tinydb import TinyDB, Query
from random import randrange, choice
from src.core.config import config

input_csv = config.get('proxies.input_csv')
db_path = config.get('proxies.db_path')
prefer_fresh_rate = config.get('proxies.prefer_fresh.rate')
healthy_max_age = config.get('proxies.healthy.max_age')
retry_tolerated_failure_count = config.get('proxies.retry.tolerated_failure.count')
retry_tolerated_failure_rate = config.get('proxies.retry.tolerated_failure.rate')
db = TinyDB(db_path)

with open(input_csv) as f:
    for line in f.read().splitlines():
        db.upsert({'proxy': line}, Query().proxy == line)

async def run_task(task):
    proxy = _pick()
    try:
        await task(proxy)
        _feedback(proxy, True)
    except Exception as e:
        _feedback(proxy, False)

def _feedback(proxy: str, succeeded: bool):
    print(f'proxy {proxy} {'succeeded' if succeeded else 'failed'}')
    if records := db.search(Query().proxy == proxy):
        record = records[0]
        record['count_usages'] = record.get('count_usages', 0) + 1
        record['last_used'] = datetime.datetime.now().timestamp()
        if succeeded:
            record['count_successes'] = record.get('count_successes', 0) + 1
            record['last_succeeded'] = record['last_used']
        db.update(record, Query().proxy == proxy)

def _pick():
    record = _pick_record()
    return record['proxy'] if record else None

def _pick_record():
    categorized = _categorize(db.all())
    healthy = categorized['healthy']
    never_used = categorized['never_used']
    retriable = categorized['retriable']
    if randrange(0, 10) < prefer_fresh_rate:
        return _pick_random(never_used) or _pick_oldest(retriable) or _pick_oldest(healthy)
    else:
        return _pick_oldest(healthy) or _pick_random(never_used) or _pick_oldest(retriable)
        #FIXME same proxy being picked by all parallel screenshots

def _categorize(_list):
    return {
        "healthy": [x for x in _list if _is_healthy(x)],
        "never_used": [x for x in _list if _is_never_used(x)],
        "retriable": [x for x in _list if _is_retriable(x)],
    }

def _pick_oldest(_list):
    return sorted(_list, key=lambda x: x['last_used'], reverse=True)[0] if _list else None

def _pick_random(_list):
    return choice(_list) if _list else None

def _is_never_used(record):
    return record.get('last_used') is None

def _is_healthy(record):
    return not _is_never_used(record) and record.get('last_used') - record.get('last_succeeded', 0) < healthy_max_age

def _is_retriable(record):
    if _is_never_used(record) or _is_healthy(record):
        return False
    else:
        count_failures = record.get('count_usages', 0) - record.get('count_successes', 0)
        ratio_failure = count_failures / record.get('count_usages', 0)
        return count_failures < retry_tolerated_failure_count or ratio_failure < retry_tolerated_failure_rate

def _print_report():
    all_proxies = db.all()
    categorized = _categorize(all_proxies)
    healthy = len(categorized['healthy'])
    never_used = len(categorized['never_used'])
    discarded = len(all_proxies) - healthy - never_used - len(categorized['retriable'])
    print(f'{len(all_proxies)} known proxies: {healthy} healthy, {never_used} never used, {discarded} discarded')

_print_report()