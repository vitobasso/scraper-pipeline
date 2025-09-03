from src.scraper.pipelines import reit_br, stock_br

_pipes = stock_br.active + reit_br.active

pipes = [p.pipeline() for p in _pipes]
