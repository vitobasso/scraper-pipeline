import asyncio
import os
import signal
from pathlib import Path

alarm_seconds = 3600 * 24
scraper_pid = Path("/tmp/scraper.pid")
api_pid = Path("/tmp/api.pid")


def scraper_wait():
    _sync_wait(signal.SIGUSR1, scraper_pid)


def scraper_notify():
    _sync_notify(signal.SIGUSR1, scraper_pid)


async def api_wait():
    await _async_wait(signal.SIGUSR2, api_pid)


def api_notify():
    _sync_notify(signal.SIGUSR2, api_pid)


def _sync_wait(sig: signal.Signals, pid_file: Path):
    signal.signal(sig, lambda _signum, _frame: None)
    with pid_file.open("w") as f:
        f.write(str(os.getpid()))
    signal.alarm(alarm_seconds)
    signal.pause()


def _sync_notify(sig: signal.Signals, pid_file: Path):
    try:
        with pid_file.open("r") as f:
            pid = int(f.read().strip())
        os.kill(pid, sig)
    except Exception as e:
        print(f"Failed to notify scraper: {e}")


event = asyncio.Event()


async def _async_wait(sig: signal.Signals, pid_file: Path):
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(sig, lambda: event.set())
    with pid_file.open("w") as f:
        f.write(str(os.getpid()))
    await event.wait()
    event.clear()
