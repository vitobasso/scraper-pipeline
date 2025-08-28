from src.scraper.active_pipes import pipes
from src.scraper.core.scheduler import Pipeline


def report_status(pipelines: list[Pipeline]):
    print(f"# {'pipeline':<20} {'available':>8} {'waiting':>8} {'ready':>8} {'aborted':>8}")
    for pipe in pipelines:
        prog = pipe.progress()
        available = len(prog.available())
        waiting = len(prog.waiting)
        ready = len(prog.ready)
        aborted = len(prog.aborted)
        print(f"{pipe.name:<22} {available:>8} {waiting:>8} {ready:>8} {aborted:>8}")
    print()


if __name__ == "__main__":
    report_status(pipes)
