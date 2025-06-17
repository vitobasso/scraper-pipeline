import calendar
from datetime import datetime
from src.services.google_sheets import copy_file, find_worksheet_by_title
from src.pipelines import yahoo, simplywall, statusinvest, statusinvest_carteira_xlsx

template_id = '1eWwqMZr4PeuH5siVoICz_XPcWVE8dGEgx_jKaarZ_4Y'  # TODO export to file and make it a local resource?


def create_spreadsheet():
    timestamp = datetime.now().strftime('%Y-%m')
    spreadsheet = copy_file(template_id, f'screening acoes-br {timestamp}')
    _populate_constants(spreadsheet)
    _populate_screening(spreadsheet)
    _populate_forecast(spreadsheet)
    _populate_statusinvest(spreadsheet)
    _populate_carteira(spreadsheet)


def _populate_constants(spreadsheet):
    worksheet = find_worksheet_by_title(spreadsheet, 'constants')
    timestamp = _last_day_of_month().strftime('%d/%m/%Y')
    worksheet.update("B1", [[timestamp]], value_input_option='USER_ENTERED')


def _populate_screening(spreadsheet):
    with open('input/ticker-list/acoes-br.csv', 'r') as file:
        tickers = [[line.strip()] for line in file.readlines()]
        worksheet = find_worksheet_by_title(spreadsheet, 'screening')
        worksheet.update("A3", tickers)


# TODO tradingview, tipranks
def _populate_forecast(spreadsheet):
    ya_data = yahoo.to_spreadsheet()
    sw_data = simplywall.to_spreadsheet()
    tickers = sorted(set(ya_data.keys()) | set(sw_data.keys()))
    combined_data = [_forecast_row(ticker, ya_data.get(ticker, {}), sw_data.get(ticker, {})) for ticker in tickers]
    worksheet = find_worksheet_by_title(spreadsheet, 'forecast')
    worksheet.update("A3", combined_data)


def _forecast_row(ticker, ya, sw):
    yr = ya.get('analyst_rating', {})
    yp = ya.get('price_forecast', {})
    return [
        ticker,
        sw.get('value', ''), sw.get('future', ''), sw.get('past', ''), sw.get('health', ''), sw.get('dividend', ''),
        yr.get('strong_buy', ''), yr.get('buy', ''), yr.get('hold', ''), yr.get('underperform', ''), yr.get('sell', ''),
        yp.get('min', ''), yp.get('avg', ''), yp.get('max', '')
    ]


def _populate_statusinvest(spreadsheet):
    worksheet = find_worksheet_by_title(spreadsheet, 'statusinvest')
    data = statusinvest.to_spreadsheet()
    worksheet.update(values=data)


def _populate_carteira(spreadsheet):
    worksheet = find_worksheet_by_title(spreadsheet, 'carteira')
    data = statusinvest_carteira_xlsx.to_spreadsheet_acoes()
    worksheet.update(values=data)


def _last_day_of_month():
    today = datetime.now()
    _, last_day = calendar.monthrange(today.year, today.month)
    return datetime(today.year, today.month, last_day)
