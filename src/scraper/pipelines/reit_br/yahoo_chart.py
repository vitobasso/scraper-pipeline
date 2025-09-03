from src.scraper.pipelines import common


def pipeline():
    return common.yahoo_chart.from_caller()
