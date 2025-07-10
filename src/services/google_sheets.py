import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery

_sheet = None
_drive = None


def _get_spread():
    if not _sheet:
        _init()
    return _sheet


def _get_drive():
    if not _drive:
        _init()
    return _drive


def _init():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("gcp-secret.json", scope)
    global _sheet, _drive
    _sheet = gspread.authorize(creds)
    _drive = discovery.build('drive', 'v3', credentials=creds)


def copy_file(id, new_name: str):
    original = _get_spread().open_by_url(f'https://docs.google.com/spreadsheets/d/{id}')
    original_permission = next(
        (perm for perm in original.list_permissions() if perm.get('role') == 'owner'),
        None  # Default if not found
    )
    new_file = _get_spread().copy(original.id, title=new_name)
    new_permission = new_file.share(email_address=original_permission['emailAddress'], perm_type='user', role='writer',
                                    notify=False)
    new_file.transfer_ownership(new_permission.json()['id'])
    return new_file


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
