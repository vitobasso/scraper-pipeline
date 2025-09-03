from src.scraper.pipelines import reit_br, stock_br

_pipes = [
    stock_br.b3_listagem,
    stock_br.investidor10,
    stock_br.simplywall,
    stock_br.statusinvest,
    stock_br.tradingview,
    stock_br.yahoo,
    stock_br.yahoo_chart,
    stock_br.yahoo_recommendations,
    reit_br.fundamentus,
    reit_br.yahoo_chart,
]

pipes = [p.pipeline() for p in _pipes]
