import datetime, csv, re
from src.core.google_sheets import copy_file, add_worksheet

template_id = '1kFkYWp_ZflNbYC0QeSRAiILiPjOTvr-81A6YJ1eS92I'

def create_spreadsheet():
    data = _load_statusinvest_data()
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    spreadsheet = copy_file(template_id, f'screening-{timestamp}')
    add_worksheet(spreadsheet, 'statusinvest', data)

def _load_statusinvest_data():
    with open('output/downloads/statusinvest-20250602T214159.csv', 'r') as file:
        rows = [row for row in csv.reader(file, delimiter=';')]
        return _clean_statusinvest_data(rows)

def _clean_statusinvest_data(data):
    return [
        [_clean_value(value) for value in row]
        for row in data
    ]

def _clean_value(value):
    replaced = str(value).replace(".", "").replace(",", ".")
    return convert_if_number(replaced)

def convert_if_number(value):
    if isinstance(value, str) and re.fullmatch(r'^-?\d+\.?\d*$', value):
        return float(value)
    return value