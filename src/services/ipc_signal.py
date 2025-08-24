import os
import signal
from pathlib import Path

alarm_seconds = 3600 * 24
pid_file = Path("/tmp/scraper.pid")


def _init():
    signal.signal(signal.SIGUSR1, lambda _signum, _frame: None)
    with pid_file.open("w") as f:
        f.write(str(os.getpid()))


def wait_for_signal():
    _init()
    print("*** waiting for signal ***")
    signal.alarm(alarm_seconds)
    signal.pause()
    print("*** woke up ***")


def wake_scraper():
    try:
        with pid_file.open("r") as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGUSR1)
    except Exception as e:
        print(f"Failed to notify scraper: {e}")
