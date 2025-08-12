from src.active_pipes import pipes

from src import config


if __name__ == '__main__':
    config.print_me()

    for i in range(200):
        for p in pipes:
            p.schedule_next()

    # statusinvest_carteira_xlsx.import_all()

