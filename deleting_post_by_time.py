import sheets_api
import time

from vk import delete_post
from dotenv import load_dotenv
from datetime import datetime
from environs import env
from sending_tg import delete_post_in_tg
from telebot.apihelper import ApiTelegramException
from requests.exceptions import ReadTimeout
from dateutil.parser import parse


def main():
    load_dotenv()
    spreadsheet_id = env.str('SPREADSHEET_ID')
    client = sheets_api.get_client()
    records = sheets_api.get_all_records(client, spreadsheet_id)
    deleting_posts = sheets_api.filter_posts_by_status(
        records,
        sheets_api.STATUS_PUBLISHED)
    now = datetime.now()
    posts = []
    for post in deleting_posts:
        if post.get('DATE & TIME TO DELETE'):
            posts.append(post)
            posts = sorted(
                posts,
                key=lambda x: x['DATE & TIME TO DELETE'],
                reverse=True)
    for post in posts:
        errors = []
        deletion_statuses = []
        row = post.get('ID')
        deletion_time = parse(post['DATE & TIME TO PUBLICATION'])
        if deletion_time > now:
            delay = now - deletion_time
            total_sec = delay.total_seconds()
            time.sleep(int(total_sec))
        if 'TG' in post.get('PLATFORM'):
            try:
                delete_post_in_tg(post['ID'])
            except ReadTimeout:
                error_description = "ТГ: ошибка подключения"
                errors.append(error_description)
                deletion_statuses.append(False)
            except ApiTelegramException as error:
                if error.error_code == 401:
                    error_description = "ТГ: ошибка авторизации бота"
                    errors.append(error_description)
                    deletion_statuses.append(False)
                if error.error_code == 400:
                    error_description = "ТГ: чат с таким ID не найден"
                    errors.append(error_description)
                    deletion_statuses.append(False)
            else:
                deletion_statuses.append(True)
        if 'VK' in post.get('PLATFORM'):
            delete_post(post['ID'])
            deletion_statuses.append(True)
        if errors:
            sheets_api.update_post_error(
                client,
                spreadsheet_id,
                row,
                ', '.join(errors))
        if deletion_statuses:
            if True in deletion_statuses:
                sheets_api.update_post_status(
                    client,
                    spreadsheet_id,
                    row,
                    sheets_api.STATUS_DELETED)
            else:
                sheets_api.update_post_status(
                    client,
                    spreadsheet_id,
                    row,
                    sheets_api.STATUS_DELETED)
        if errors:
            sheets_api.update_post_error(
                client,
                spreadsheet_id,
                row,
                ', '.join(errors))


if __name__ == "__main__":
    main()
