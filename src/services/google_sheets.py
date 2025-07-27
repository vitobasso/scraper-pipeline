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


def list_files():
    about = _get_drive().about().get(fields="storageQuota").execute()
    print(about['storageQuota'])
    files = _get_drive().files().list(pageSize=100,
                                      fields="files(id, name, size, createdTime, trashed, webViewLink)").execute()
    for f in sorted(files.get('files', []), key=lambda x: int(x.get('cratedTime', 0)), reverse=True):
        if f['id'] not in keep:
            print('delete', f['createdTime'], f.get('size'), f['name'], f['webViewLink'])
            # _get_drive().files().delete(fileId=f['id']).execute()
        else:
            print('keep  ', f['createdTime'], f.get('size'), f['name'], f['webViewLink'])

    # _get_drive().files().emptyTrash().execute()


keep = [
    "1eWwqMZr4PeuH5siVoICz_XPcWVE8dGEgx_jKaarZ_4Y",  # template
    "1RIajiids3rYC_b_p0J26GD9hEimbzaw5Zg8ZkSwYPq8",  # template
    "12sjcvppRdmd_TLoKau2gyQjktl9bzu6zZw3HUzOAG-4",
    "1Qzixz5f0U9ZS1_L_AO_RQD5ZMruuBsAen1_LPSkTE2k",
    "1OE7fn003bhYP3Ip_u5-B0bmIk2ioVhOgJ8U92dnWlsk",
    "1qlNYr8_BF2IoDolAcfWSx298pPI2IP4gY4z3M7MEfVU",
    "1_DryVet9uRYBkvmQQ79FNSW5gsNOGV-W2XB4_BmEjvw",
    "1pI4WnEk1rZdtT9lUm2T20wOl7zp5hPBtkCVwj0vTQHY",
    "1lfSkRv5bGhUyba1ZxKpOAYDZnN5Jb4Z6sKjrQMwEmDU",
    "15ZH6DHlfHrUwsATY4uWMBDVWAEo53_kEJtkG5bc0lW8",
]
