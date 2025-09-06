import random

from src.common import config
from src.common.services import ipc_signal
from src.scraper.pipelines import reit_br, stock_br

pipes = [p.pipeline() for p in stock_br.active + reit_br.active]


def main():
    config.print_me()

    while True:
        pending = [p for p in pipes if not p.is_done()]
        if pending:
            p = random.choice(pending)
            p.run_next()
        else:
            ipc_signal.wait_for_signal()


if __name__ == "__main__":
    main()
