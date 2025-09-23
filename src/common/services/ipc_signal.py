import os
import signal
from pathlib import Path

alarm_seconds = 3600 * 24
scraper_pid = Path("/tmp/scraper.pid")
api_pid = Path("/tmp/api.pid")


def scraper_wait():
    _wait(signal.SIGUSR1, scraper_pid)


def scraper_notify():
    _notify(signal.SIGUSR1)


def _init(sig: signal.Signals, pid_file: Path):
    signal.signal(sig, lambda _signum, _frame: None)
    with pid_file.open("w") as f:
        f.write(str(os.getpid()))


def _wait(sig: signal.Signals, pid_file: Path):
    _init(sig, pid_file)
    signal.alarm(alarm_seconds)
    signal.pause()


def _notify(sig: signal.Signals):
    try:
        with scraper_pid.open("r") as f:
            pid = int(f.read().strip())
        os.kill(pid, sig)
    except Exception as e:
        print(f"Failed to notify scraper: {e}")
