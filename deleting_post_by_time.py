import sheets_api
import time

from vk import delete_post
from dotenv import load_dotenv
from datetime import datetime
from environs import Env
from sending_tg import delete_post_in_tg
from telebot.apihelper import ApiTelegramException
from requests.exceptions import ReadTimeout
from dateutil.parser import parse
from vk_api.exceptions import ApiError


def main():
    env = Env()
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
        if post.get('delete_time'):
            posts.append(post)
            posts = sorted(
                posts,
                key=lambda x: x['delete_time'],
                reverse=True)
    for post in posts:
        row = post.get('row')
        deletion_time = parse(post['delete_time'])
        if deletion_time > now:
            delay = deletion_time - now
            total_sec = delay.total_seconds()
            time.sleep(int(total_sec))
        if 'TG' in post.get('platform'):
            errors = []
            try:
                delete_post_in_tg(post['id'])
            except ReadTimeout:
                error_description = "ТГ: ошибка подключения"
                errors.append(error_description)
            except ApiTelegramException as error:
                if error.error_code == 401:
                    error_description = "ТГ: ошибка авторизации бота"
                    errors.append(error_description)
                if error.error_code == 400:
                    error_description = "ТГ: чат с таким ID не найден"
                    errors.append(error_description)
            else:
                sheets_api.update_post_status(
                    client,
                    spreadsheet_id,
                    row,
                    sheets_api.STATUS_DELETED)
        if 'VK' in post.get('platform'):
            errors = []
            try:
                delete_post(post['id'])
            except ReadTimeout:
                error_description = "VK: ошибка подключения"
                errors.append(error_description)
            except ApiError as e:
                error_description = f"VK: {e}"
                if e.code == 5:
                    error_description += "\nОшибка доступа"
                    " - неверный токен или недостаточно прав."
                elif e.code == 15:
                    error_description += "\nОшибка приложения - недостаточно прав."
                errors.append(error_description)
        if errors:
            sheets_api.update_post_error(
                client,
                spreadsheet_id,
                row,
                ', '.join(errors))
        else:
            sheets_api.update_post_status(
                client,
                spreadsheet_id,
                row,
                sheets_api.STATUS_DELETED)


if __name__ == "__main__":
    main()
