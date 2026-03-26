import os
from dotenv import load_dotenv
import sheets_api
import sending_ok


def main():
    load_dotenv()
    spreadsheet_id = os.environ['SPREADSHEET_ID']

    client = sheets_api.get_client()
    records = sheets_api.get_all_records(client, spreadsheet_id)
    posts = sheets_api.filter_posts_by_status(records, sheets_api.STATUS_PENDING)
    # print(posts)

    for post in posts:
        if 'OK' in post.get('platform'):
            status = publish_post_ok(post)
            print(status)
        if 'TG' in post.get('platform'):
            print('TG')
        if 'VK' in post.get('platform'):
            print('VK')
    row = 3
    sheets_api.update_post_status(
        client,
        spreadsheet_id,
        row,
        sheets_api.STATUS_PUBLISHED)
    sheets_api.update_post_error(client, spreadsheet_id, row, "Какая-то ошибка")


if __name__ == "__main__":
    main()