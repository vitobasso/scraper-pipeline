import random

from src import config
from src.active_pipes import pipes
from src.services import ipc_signal

if __name__ == "__main__":
    config.print_me()

    while True:
        pending = [p for p in pipes if not p.is_done()]
        if pending:
            p = random.choice(pending)
            p.run_next()
        else:
            ipc_signal.wait_for_signal()
