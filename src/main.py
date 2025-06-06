# from src.core.proxies import random_proxy
# from src.flows.image_extract import extract_analysis, extract_fundamentals
# import src.spreadsheet.screening_sheet as screening_sheet
from src.flows import yahoo, tradingview, investidor10, b3idiv, statusinvest, generic_screenshot
import scheduler

if __name__ == '__main__':
    for i in range(100):
        scheduler.schedule_next(yahoo.flow())
    # yahoo.extract_analysis('output/screenshots/consumed/yahoo-bbas3-20250605T180728.png')
    # proxy = random_proxy()
    # ticker_screenshot.screenshot_yahoo_br('bbas3')
    # ticker_screenshot.screenshot_simplywall()
    # statusinvest.sync_download()
    # b3idiv.sync_download()
    # extract_analysis("output/screenshots/valid/tradingview-BMFBOVESPA-PETR4-20250530T184949.png")
    # extract_analysis("output/screenshots/valid/tipranks-qqq-20250530T180430.png")
    # extract_fundamentals("output/screenshots/valid/investidor10-bbas3-20250601T155718.png")
    # screening_sheet.create_spreadsheet()
    # yahoo.compile_data()
    pass
