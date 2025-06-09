import csv, re, calendar
from datetime import datetime
from src.core.google_sheets import copy_file, find_worksheet_by_title
from src.flows import yahoo, simplywall

template_id = '1eWwqMZr4PeuH5siVoICz_XPcWVE8dGEgx_jKaarZ_4Y'  # TODO export to file and make it a local resource?


def create_spreadsheet():
    timestamp = datetime.now().strftime('%Y-%m')
    spreadsheet = copy_file(template_id, f'screening {timestamp}')
    _populate_constants(spreadsheet)
    _populate_screening(spreadsheet)
    _populate_forecast(spreadsheet)
    _populate_statusinvest(spreadsheet)
    _populate_simplywall(spreadsheet) # TODO do per stock instead


def _populate_constants(spreadsheet):
    worksheet = find_worksheet_by_title(spreadsheet, 'constants')
    timestamp = _last_day_of_month().strftime('%d/%m/%Y')
    worksheet.update("B1", [[timestamp]], value_input_option='USER_ENTERED')


def _populate_screening(spreadsheet):
    with open('input/ticker-list/acoes-br.csv', 'r') as file:
        tickers = [[line.strip()] for line in file.readlines()]
        worksheet = find_worksheet_by_title(spreadsheet, 'screening')
        worksheet.update("A3", tickers)


def _populate_forecast(spreadsheet):
    data = yahoo.to_spreadsheet() # TODO tradingview, tipranks
    worksheet = find_worksheet_by_title(spreadsheet, 'forecast')
    worksheet.update("A3", data)


def _populate_statusinvest(spreadsheet):
    worksheet = find_worksheet_by_title(spreadsheet, 'statusinvest')
    data = _load_statusinvest_data()
    worksheet.update(values=data)


def _populate_simplywall(spreadsheet):
    worksheet = find_worksheet_by_title(spreadsheet, 'simplywall')
    data = simplywall.to_spreadsheet('br')
    worksheet.update(values=data)


def _load_statusinvest_data():
    with open('output/20250605/downloads/statusinvest-20250602T214159.csv', 'r') as file:  # TODO dynamic path
        rows = [row for row in csv.reader(file, delimiter=';')]
        return _clean_statusinvest_data(rows)


# TODO move to statusinvest.py
def _clean_statusinvest_data(data):
    return [
        [_clean_numbers(value) for value in row]
        for row in data
    ]


def _clean_numbers(value):
    replaced = str(value).replace(".", "").replace(",", ".")
    return _convert_if_number(replaced)


def _convert_if_number(value):
    if isinstance(value, str) and re.fullmatch(r'^-?\d+\.?\d*$', value):
        return float(value)
    return value


def _last_day_of_month():
    today = datetime.now()
    _, last_day = calendar.monthrange(today.year, today.month)
    return datetime(today.year, today.month, last_day)
