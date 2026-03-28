import os
from dotenv import load_dotenv
import sheets_api
from sending_tg import sending_post_in_tg, delete_post_in_tg


def main():
    load_dotenv()
    spreadsheet_id = os.environ['SPREADSHEET_ID']

    client = sheets_api.get_client()
    records = sheets_api.get_all_records(client, spreadsheet_id)
    posts = sheets_api.filter_posts_by_status(records, sheets_api.STATUS_PENDING)
    
    row = 3
    sheets_api.update_post_status(
        client,
        spreadsheet_id,
        row,
        sheets_api.STATUS_PUBLISHED)
    sheets_api.update_post_error(client, spreadsheet_id, row, "Какая-то ошибка")
    delete_post_in_tg('1')


if __name__ == "__main__":
    main()