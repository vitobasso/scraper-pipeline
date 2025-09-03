from src.scraper.pipelines.common import yahoo_chart


def pipeline():
    return yahoo_chart.from_caller()
