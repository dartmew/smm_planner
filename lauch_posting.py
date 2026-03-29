import os
from dotenv import load_dotenv
import sheets_api
from sending_ok import publish_post_ok
from sending_tg import sending_post_in_tg
from telebot.apihelper import ApiTelegramException
from requests.exceptions import ReadTimeout


def main():
    load_dotenv()
    spreadsheet_id = os.environ['SPREADSHEET_ID']
    client = sheets_api.get_client()
    records = sheets_api.get_all_records(client, spreadsheet_id)
    pending_posts = sheets_api.filter_posts_by_status(
        records,
        sheets_api.STATUS_PENDING,
    )
    posts = []
    for post in pending_posts:
        if not post.get('publicate_time'):
            posts.append(post)
    for post in posts:
        errors = []
        publication_statuses = []
        row = post.get('row')
        if 'OK' in post.get('platform'):
            try:
                publish_post_ok(post)
            except KeyError:
                error_description = 'ОК: ошибка подключения'
                errors.append(error_description)
                publication_statuses.append(False)
            else:
                publication_statuses.append(True)
        if 'TG' in post.get('platform'):
            try:
                sending_post_in_tg(post)
            except ReadTimeout:
                error_description = "ТГ: ошибка подключения"
                errors.append(error_description)
                publication_statuses.append(False)
            except ApiTelegramException as error:
                if error.error_code == 401:
                    error_description = "ТГ: ошибка авторизации бота"
                    errors.append(error_description)
                    publication_statuses.append(False)
                if error.error_code == 400:
                    error_description = "ТГ: чат с таким ID не найден"
                    errors.append(error_description)
                    publication_statuses.append(False)
            else:
                publication_statuses.append(True)
        if 'VK' in post.get('platform'):
            send_to_vk()
            publication_statuses.append(True)
        if errors:
            sheets_api.update_post_error(client, spreadsheet_id, row, ', '.join(errors))
        if publication_statuses:
            if True in publication_statuses:
                sheets_api.update_post_status(
                    client,
                    spreadsheet_id,
                    row,
                    sheets_api.STATUS_PUBLISHED)
            else:
                sheets_api.update_post_status(
                    client,
                    spreadsheet_id,
                    row,
                    sheets_api.STATUS_ERROR)


if __name__ == "__main__":
    main()
