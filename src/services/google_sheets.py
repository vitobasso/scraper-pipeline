import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery, http
from src.config import gdrive_dir
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


def new_file(template: str, file_name: str):
    file_metadata = {'name': file_name, 'parents': [gdrive_dir], 'mimeType': 'application/vnd.google-apps.spreadsheet'}
    media = http.MediaFileUpload(template, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    new_file = _get_drive().files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return _get_sheet().open_by_key(new_file['id'])


def find_worksheet_by_title(spreadsheet, title: str):
    return next((x for x in spreadsheet.worksheets() if x.title == title), None)
