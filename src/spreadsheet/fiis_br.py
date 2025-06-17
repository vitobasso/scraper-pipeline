import calendar
from datetime import datetime
from src.services.google_sheets import copy_file, find_worksheet_by_title
from src.pipelines import fundamentus_fiis, statusinvest_carteira_xlsx

template_id = '1RIajiids3rYC_b_p0J26GD9hEimbzaw5Zg8ZkSwYPq8'  # TODO export to file and make it a local resource?


def create_spreadsheet():
    timestamp = datetime.now().strftime('%Y-%m')
    spreadsheet = copy_file(template_id, f'screening fiis-br {timestamp}')
    _populate_constants(spreadsheet)
    _populate_screening(spreadsheet)
    _populate_fundamentus(spreadsheet)
    _populate_carteira(spreadsheet)


def _populate_constants(spreadsheet):
    worksheet = find_worksheet_by_title(spreadsheet, 'constants')
    timestamp = _last_day_of_month().strftime('%d/%m/%Y')
    worksheet.update("B1", [[timestamp]], value_input_option='USER_ENTERED')


def _populate_screening(spreadsheet):
    with open('input/ticker-list/fiis-br.csv', 'r') as file:
        tickers = [[line.strip()] for line in file.readlines()]
        worksheet = find_worksheet_by_title(spreadsheet, 'screening')
        worksheet.update("A3", tickers)


def _populate_fundamentus(spreadsheet):
    worksheet = find_worksheet_by_title(spreadsheet, 'fundamentus')
    data = fundamentus_fiis.to_spreadsheet()
    worksheet.update(values=data)


def _populate_carteira(spreadsheet):
    worksheet = find_worksheet_by_title(spreadsheet, 'carteira')
    data = statusinvest_carteira_xlsx.to_spreadsheet_fiis()
    worksheet.update(values=data)


def _last_day_of_month():
    today = datetime.now()
    _, last_day = calendar.monthrange(today.year, today.month)
    return datetime(today.year, today.month, last_day)
