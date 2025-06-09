from scheduler import schedule_next, report
from src.flows import yahoo, tradingview, tipranks, simplywall, statusinvest
from src.spreadsheet.screening_sheet import create_spreadsheet

acoes_br = 'input/ticker-list/acoes-br.csv'

if __name__ == '__main__':
    for i in range(400):
        schedule_next(yahoo.pipeline(acoes_br))
        schedule_next(tradingview.pipeline(acoes_br))
        schedule_next(simplywall.pipeline(acoes_br))
        # schedule_next(tipranks.pipeline('input/ticker-list/stocks-us.csv'))
        # schedule_next(statusinvest.pipeline())
    # simplywall.aggregate('br')
    # proxy = random_proxy()
    # yahoo.compile_data()
    # yahoo.validate_data('output/20250606/data/awaiting-validation/yahoo-cmig4-20250606T122342.json')
    # create_spreadsheet()

    report(yahoo.pipeline(acoes_br))
    report(tradingview.pipeline(acoes_br))
    report(simplywall.pipeline(acoes_br))
    pass
