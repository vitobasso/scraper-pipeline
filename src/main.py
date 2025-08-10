from src.pipelines import *
from src.scheduler import report

csv_acoes_br = 'input/ticker-list/acoes-br.csv'

if __name__ == '__main__':
    pipes = [
        fundamentus_fiis.pipeline(),
        investidor10.pipeline(csv_acoes_br),
        simplywall.pipeline(csv_acoes_br),
        statusinvest.pipeline(),
        # tipranks.pipeline('input/ticker-list/stocks-us.csv'),
        tradingview.pipeline(csv_acoes_br),
        yahoo.pipeline(csv_acoes_br),
        yahoo_chart.pipeline(csv_acoes_br),
        yahoo_recomendations.pipeline(csv_acoes_br),
    ]

    report(pipes)
    for i in range(200):
        for p in pipes:
            p.schedule_next()
    report(pipes)

    # statusinvest_carteira_xlsx.import_all()

