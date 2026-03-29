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


def get_client():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client


def get_all_records(client, spreadsheet_id):
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
                'publicate_time': record.get('DATE & TIME TO PUBLICATION'),
                'platform': record.get('PLATFORM'),
                'text': record.get('TEXT'),
                'media_link': record.get('MEDIA LINK'),
                'delete_time': record.get('DATE & TIME TO DELETE'),
                'status': record.get('STATUS'),
                'error_description': record.get('ERROR_DESCRIPTION')
            })
    return posts


def update_post_status(client, spreadsheet_id, row, new_status):
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


def update_post_error(client, spreadsheet_id, row, error_message):
    sheet = client.open_by_key(spreadsheet_id).sheet1
    headers = sheet.row_values(1)
    error_col_index = headers.index('ERROR DESCRIPTION') + 1
    sheet.update_cell(row, error_col_index, error_message)
