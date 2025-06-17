import pandas as pd, csv, re
from src.common.util import mkdir, timestamp, all_files
from src.config import output_root

name = 'statusinvest_carteira'
output_dir = mkdir(f'{output_root}/{name}')
input_dir = 'input/statusinvest'


def import_all():
    xlsx_path = all_files(input_dir)[0]
    _import(xlsx_path, 'Ações', f'{output_dir}/acoes-{timestamp()}.csv')
    _import(xlsx_path, 'FIIs', f'{output_dir}/fiis-{timestamp()}.csv')


def _import(xlsx_path: str, sheet_name: str, output_path: str):
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
    df.to_csv(output_path, index=False)


def to_spreadsheet_acoes():
    return _to_spreadsheet('acoes')


def to_spreadsheet_fiis():
    return _to_spreadsheet('fiis')


def _to_spreadsheet(prefix):
    files = [file for file in all_files(output_dir) if prefix in file]
    if files:
        with open(files[0]) as file:
            return [[_convert_if_number(value) for value in row]
                    for row in csv.reader(file)]
    else:
        return []


def _convert_if_number(value):
    if isinstance(value, str) and re.fullmatch(r'^-?\d+\.?\d*$', value):
        return float(value)
    return value
