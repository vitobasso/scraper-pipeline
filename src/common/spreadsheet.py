import json
from src.common.util import filename_before_timestamp, all_files


def json_to_spreadsheet(dir_path, transform_data=lambda x:x):
    def _entry(path):
        ticker = filename_before_timestamp(path)
        with open(path) as file:
            data = json.load(file)
            return ticker, transform_data(data)

    return dict(_entry(path) for path in all_files(dir_path))