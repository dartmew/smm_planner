import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from io import BytesIO


STATUS_PENDING = 'pending'
STATUS_PUBLISHED = 'published'
STATUS_ERROR = 'error'
STATUS_DELETED = 'deleted'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
CREDENTIALS_FILE = 'credentials.json'


def get_credentials():
    return Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)


def get_client():
    creds = get_credentials()
    return gspread.authorize(creds)


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


def download_drive_files_to_memory(media_link):
    if not media_link:
        return []
    
    if ',' in media_link:
        links = [link.strip() for link in media_link.split(',')]
    else:
        links = media_link.split()
    buffers = []

    for link in links:
        if link:
            buffers.append(_download_single_file(link))
    
    return buffers


def _download_single_file(media_link):
    creds = get_credentials()
    
    if '/d/' in media_link:
        file_id = media_link.split('/d/')[1].split('/')[0]
    elif 'id=' in media_link:
        file_id = media_link.split('id=')[1].split('&')[0]
    else:
        raise ValueError(f"Не могу извлечь ID из ссылки: {media_link}")
    
    drive_service = build('drive', 'v3', credentials=creds)
    request = drive_service.files().get_media(fileId=file_id)
    file_buffer = BytesIO()
    downloader = MediaIoBaseDownload(file_buffer, request)
    done = False
    
    while not done:
        status, done = downloader.next_chunk()
    file_buffer.seek(0)
    
    return file_buffer