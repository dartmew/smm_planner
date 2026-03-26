import sheets_api

from environs import env
from dotenv import load_dotenv
from sending_tg import sending_img_in_tg


def main():
    load_dotenv()
    spreadsheet_id = env.str('SPREADSHEET_ID')

    # Поулчение записей из таблицы
    records = sheets_api.get_all_records(spreadsheet_id)
    # Получение постов для публикации
    pending = sheets_api.filter_posts_by_status(records, sheets_api.STATUS_PENDING)
    
    # Обновление статуса в строке таблицы
    row = 3
    
    sheets_api.update_post_status(spreadsheet_id, row, sheets_api.STATUS_PUBLISHED)
    sending_img_in_tg(pending)

if __name__ == "__main__":
    main()