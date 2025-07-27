import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
from src.config import google_dir
from google_auth_oauthlib.flow import InstalledAppFlow

_sheet = None
_drive = None


def _get_sheet():
    global _sheet
    if not _sheet:
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name("gcp-secret.json", scope)
        _sheet = gspread.authorize(creds)
    return _sheet


def _get_drive():
    global _drive
    if not _drive:
        scope = ['https://www.googleapis.com/auth/drive']
        flow = InstalledAppFlow.from_client_secrets_file('client-secret.json', scope)
        creds = flow.run_local_server(port=0)
        _drive = discovery.build('drive', 'v3', credentials=creds)
    return _drive


def copy_file(original_id, new_name: str):
    files = _get_drive().files()
    copied_file = files.copy(fileId=original_id, body={'name': new_name}).execute()
    files.update(
        fileId=copied_file['id'],
        addParents=google_dir,
        removeParents='root',
        fields='id, parents'
    ).execute()
    return _get_sheet().open_by_key(copied_file['id'])


def find_worksheet_by_title(spreadsheet, title: str):
    return next((x for x in spreadsheet.worksheets() if x.title == title), None)
