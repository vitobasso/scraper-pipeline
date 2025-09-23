from src.common import config
from src.common.services import ipc_signal
from src.common.util.date_util import timestamp
from src.scraper.core.scheduler import Manager
from src.scraper.pipelines import reit_br, stock_br

pipes = [p.pipeline() for p in stock_br.active + reit_br.active]
manager = Manager.from_pipelines(pipes)


def main():
    config.print_me()

    while True:
        if not manager.run_next():
            print(f"{timestamp()}: *** waiting for signal ***")
            ipc_signal.scraper_wait()
            print(f"{timestamp()}: *** woke up ***")


if __name__ == "__main__":
    main()
