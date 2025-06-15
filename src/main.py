from scheduler import schedule_next, report
from src.pipelines import yahoo, tradingview, tipranks, simplywall, statusinvest, fundamentus_fiis
from src.spreadsheet import acoes_br as ss_acoes_br, fiis_br

acoes_br = 'input/ticker-list/acoes-br.csv'

if __name__ == '__main__':
    # for i in range(100):
        # schedule_next(yahoo.pipeline(acoes_br))
        # schedule_next(tradingview.pipeline(acoes_br))
        # schedule_next(simplywall.pipeline(acoes_br))
        # schedule_next(tipranks.pipeline('input/ticker-list/stocks-us.csv'))
        # schedule_next(statusinvest.pipeline())
    # schedule_next(statusinvest.pipeline())
    # schedule_next(fundamentus_fiis.pipeline())
    # ss_acoes_br.create_spreadsheet()
    fiis_br.create_spreadsheet()

    # report(yahoo.pipeline(acoes_br))
    # report(tradingview.pipeline(acoes_br))
    # report(simplywall.pipeline(acoes_br))
    # report(statusinvest.pipeline())
    pass
