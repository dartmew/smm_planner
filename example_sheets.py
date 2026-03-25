import os
from dotenv import load_dotenv
import sheets_api


def main():
    load_dotenv()
    spreadsheet_id = os.environ['SPREADSHEET_ID']

    # Поулчение записей из таблицы
    records = sheets_api.get_all_records(spreadsheet_id)
    # Получение постов для публикации
    pending = sheets_api.filter_posts_by_status(records, sheets_api.STATUS_PENDING)
    print(f'pending rows: {pending}')
    # Обновление статуса в строке таблицы
    row = 3
    sheets_api.update_post_status(spreadsheet_id, row, sheets_api.STATUS_PUBLISHED)


if __name__ == "__main__":
    main()
