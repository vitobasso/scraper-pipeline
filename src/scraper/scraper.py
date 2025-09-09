from src.common import config
from src.common.services import ipc_signal
from src.scraper.core.scheduler import Manager
from src.scraper.pipelines import reit_br, stock_br

pipes = [p.pipeline() for p in stock_br.active + reit_br.active]
manager = Manager.from_pipelines(pipes)


def main():
    config.print_me()

    while True:
        if not manager.run_next():
            ipc_signal.wait_for_signal()


if __name__ == "__main__":
    main()
