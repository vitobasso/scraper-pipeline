from typing import List

from src.active_pipes import pipes
from src.core.scheduler import Pipeline


def report_status(pipelines: List[Pipeline]):
    print(f'# {"pipeline":<20} {"available":>8} {"waiting":>8} {"ready":>8} {"aborted":>8}')
    for pipe in pipelines:
        prog = pipe.progress()
        print(f'{pipe.name:<22} {len(prog.available()) :>8} {len(prog.waiting) :>8} {len(prog.ready) :>8} {len(prog.aborted) :>8}')
    print()


if __name__ == '__main__':
    report_status(pipes)
