import scheduler
from src.flows import yahoo, tradingview, tipranks
from src.spreadsheet.screening_sheet import create_spreadsheet

if __name__ == '__main__':
    for i in range(100):
        scheduler.schedule_next(tipranks.flow())
    # proxy = random_proxy()
    # yahoo.compile_data()
    # yahoo.screenshot('cmig4')
    # create_spreadsheet()
    pass
