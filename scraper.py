import random

from src.active_pipes import pipes

from src import config

if __name__ == '__main__':
    config.print_me()

    pending = list(pipes)
    while pending:
        p = random.choice(pending)
        p.run_next() if not p.is_done() else pending.remove(p)

    # statusinvest_carteira_xlsx.import_all()
