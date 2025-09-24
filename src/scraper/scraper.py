from src.common import config
from src.common.services import ipc_signal, repository
from src.common.util.date_util import timestamp
from src.scraper.core.scheduler import Manager
from src.scraper.pipelines import reit_br, stock_br

pipes = [p.pipeline() for p in stock_br.active + reit_br.active]
manager = Manager.from_pipelines(pipes)


def main():
    config.print_me()

    while True:
        task_done = manager.run_next()
        if task_done:
            if task_done.has_output():
                repository.upsert_scrape(task_done.pipeline.asset_class, task_done.task.ticker, task_done.pipeline.name)
                ipc_signal.api_notify()
        else:
            print(f"{timestamp()}: *** waiting for signal ***")
            ipc_signal.scraper_wait()
            print(f"{timestamp()}: *** woke up ***")


if __name__ == "__main__":
    main()
