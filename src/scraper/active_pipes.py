from src.scraper.pipelines import *

_pipes = [
    b3_listagem,
    investidor10,
    simplywall,
    statusinvest,
    tradingview,
    yahoo,
    yahoo_chart,
    yahoo_recommendations,
]

pipes = [p.pipeline() for p in _pipes]
