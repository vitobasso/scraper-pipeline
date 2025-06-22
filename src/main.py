from scheduler import schedule_next, report
from src.pipelines import (yahoo, tradingview, tipranks, simplywall, statusinvest, fundamentus_fiis,
                           statusinvest_carteira_xlsx, investidor10)
from src.spreadsheet import acoes_br, fiis_br

csv_acoes_br = 'input/ticker-list/acoes-br.csv'

if __name__ == '__main__':
    for i in range(100):
        schedule_next(fundamentus_fiis.pipeline())
        schedule_next(investidor10.pipeline(csv_acoes_br))
        schedule_next(simplywall.pipeline(csv_acoes_br))
        schedule_next(statusinvest.pipeline())
        # schedule_next(tipranks.pipeline('input/ticker-list/stocks-us.csv'))
        schedule_next(tradingview.pipeline(csv_acoes_br))
        schedule_next(yahoo.pipeline(csv_acoes_br))
    statusinvest_carteira_xlsx.import_all()
    acoes_br.create_spreadsheet()
    # fiis_br.create_spreadsheet()

    # report(yahoo.pipeline(csv_acoes_br))
    # report(tradingview.pipeline(csv_acoes_br))
    # report(simplywall.pipeline(csv_acoes_br))
    # report(statusinvest.pipeline())
    pass
