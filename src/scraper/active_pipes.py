from src.scraper.pipelines.reit_br import fundamentus
from src.scraper.pipelines.stock_br import (
    b3_listagem,
    investidor10,
    simplywall,
    statusinvest,
    tradingview,
    yahoo,
    yahoo_chart,
    yahoo_recommendations,
)

_pipes = [
    b3_listagem,
    investidor10,
    simplywall,
    statusinvest,
    tradingview,
    yahoo,
    yahoo_chart,
    yahoo_recommendations,
    fundamentus,
]

pipes = [p.pipeline() for p in _pipes]
