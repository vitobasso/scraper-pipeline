from src.pipelines import *
from src.spreadsheet import *

csv_acoes_br = 'input/ticker-list/acoes-br.csv'

if __name__ == '__main__':
    pipes = [
        # fundamentus_fiis.pipeline(),
        # investidor10.pipeline(csv_acoes_br),
        # simplywall.pipeline(csv_acoes_br),
        # statusinvest.pipeline(),
        # # tipranks.pipeline('input/ticker-list/stocks-us.csv'),
        # tradingview.pipeline(csv_acoes_br),
        yahoo.pipeline(csv_acoes_br),
    ]
    for i in range(100):
        for p in pipes:
            p.schedule_next()

    statusinvest_carteira_xlsx.import_all()
    # acoes_br.create_spreadsheet()
    # fiis_br.create_spreadsheet()

    for p in pipes:
        p.report()
