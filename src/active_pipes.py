from src.pipelines import *

csv_acoes_br = 'input/ticker-list/acoes-br.csv'
pipes = [
    fundamentus_fiis.pipeline(),
    investidor10.pipeline(csv_acoes_br),
    simplywall.pipeline(csv_acoes_br),
    statusinvest.pipeline(),
    tradingview.pipeline(csv_acoes_br),
    yahoo.pipeline(csv_acoes_br),
    yahoo_chart.pipeline(csv_acoes_br),
    yahoo_recomendations.pipeline(csv_acoes_br),
    # tipranks.pipeline('input/ticker-list/stocks-us.csv'),
]