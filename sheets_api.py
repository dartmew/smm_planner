import gspread
from google.oauth2.service_account import Credentials


STATUS_PENDING = 'pending'
STATUS_PUBLISHED = 'published'
STATUS_ERROR = 'error'
STATUS_DELETED = 'deleted'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
CREDENTIALS_FILE = 'credentials.json'


def _connect_to_sheets():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client


def get_all_records(spreadsheet_id):
    client = _connect_to_sheets()
    sheet = client.open_by_key(spreadsheet_id).sheet1
    all_records = sheet.get_all_records()
    filtered_records = []

    for record in all_records:
        record_id = record.get('ID')

        if record_id and str(record_id).strip():
            filtered_records.append(record)
    return filtered_records


def filter_posts_by_status(records, status_filter):
    posts = []

    for idx, record in enumerate(records, start=2):
        record_status = record.get('STATUS', '').lower()
        platform = record.get('PLATFORM', '')

        if record_status == status_filter and platform:
            posts.append({
                'row': idx,
                'id': record.get('ID'),
                'name': record.get('NAME'),
                'platform': record.get('PLATFORM'),
                'doc_link': record.get('LINK GOOGLE DOC'),
                'media_link': record.get('LINK MEDIA'),
                'delete_time': record.get('DATE & TIME TO DELETE')
            })
    return posts


def update_post_status(spreadsheet_id, row, new_status):
    client = _connect_to_sheets()
    sheet = client.open_by_key(spreadsheet_id).sheet1

    headers = sheet.row_values(1)
    status_col_index = headers.index('STATUS') + 1

    sheet.update_cell(row, status_col_index, new_status)
    print(f'Строка {row}: статус обновлен на {new_status}')


def parse_platforms(platform_string):
    if ',' in platform_string:
        platforms = [p.strip() for p in platform_string.split(',')]
    else:
        platforms = platform_string.split()
    return platforms
