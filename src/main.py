import scheduler
from src.flows import yahoo, tradingview, tipranks, simplywall, statusinvest
from src.spreadsheet.screening_sheet import create_spreadsheet

if __name__ == '__main__':
    for i in range(100):
        # scheduler.schedule_next(yahoo.pipeline('input/ticker-list/acoes-br.csv'))
        # scheduler.schedule_next(tipranks.pipeline('input/ticker-list/stocks-us.csv'))
        scheduler.schedule_next(statusinvest.pipeline())
    # simplywall.scrape()
    # proxy = random_proxy()
    # yahoo.compile_data()
    # yahoo.validate_data('output/20250606/data/awaiting-validation/yahoo-cmig4-20250606T122342.json')
    # create_spreadsheet()
    pass
