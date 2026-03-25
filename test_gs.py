import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv


load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']

def test_connection():
    print("🔐 Подключение к Google Sheets...")
    
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    
    print(f"✅ Подключено! Имя таблицы: {sheet.title}")

    records = sheet.get_all_records()
    print(f"\n📊 Найдено записей: {len(records)}")
    
    for i, row in enumerate(records, 1):
        print(f"\n--- Запись {i} ---")
        for key, value in row.items():
            print(f"  {key}: {value}")
    
    print("\n✍️ Пишу тестовый статус...")
    sheet.update_cell(1, 5, "status")
    sheet.update_cell(2, 5, "✅ тест OK")
    
    print("✅ Статус записан!")
    print(f"\n🔗 https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")

if __name__ == "__main__":
    test_connection()