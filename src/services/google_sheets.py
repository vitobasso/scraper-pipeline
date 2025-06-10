import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("gcp-secret.json", scope)
client = gspread.authorize(creds)


def copy_file(id, new_name: str):
    original = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{id}')
    original_permission = next(
        (perm for perm in original.list_permissions() if perm.get('role') == 'owner'),
        None  # Default if not found
    )
    new_file = client.copy(original.id, title=new_name)
    new_permission = new_file.share(email_address=original_permission['emailAddress'], perm_type='user', role='writer',
                                    notify=False)
    new_file.transfer_ownership(new_permission.json()['id'])
    return new_file


def find_worksheet_by_title(spreadsheet, title: str):
    return next((x for x in spreadsheet.worksheets() if x.title == title), None)
