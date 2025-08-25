from src.pipelines import *

_pipes = [
    # fundamentus_fiis,
    investidor10,
    simplywall,
    statusinvest,
    tradingview,
    yahoo,
    yahoo_chart,
    yahoo_recommendations,
]

pipes = [p.pipeline() for p in _pipes]