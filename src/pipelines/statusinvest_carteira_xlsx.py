import pandas as pd
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

