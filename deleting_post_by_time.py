import os
import sheets_api
import time

from dotenv import load_dotenv
from datetime import datetime
from environs import env
from sending_tg import delete_post_in_tg
from telebot.apihelper import ApiTelegramException
from requests.exceptions import ReadTimeout
from datetime import timedelta
from dateutil.parser import parse

 
def main():
    load_dotenv()
    spreadsheet_id = env.str('SPREADSHEET_ID')
    client = sheets_api.get_client()
    records = sheets_api.get_all_records(client, spreadsheet_id)
    pending_posts = sheets_api.filter_posts_by_status(records, sheets_api.STATUS_PENDING)
    now = datetime.now()
    posts = []
    for post in pending_posts:
        if post.get('delete_time'):
            posts.append(post)
            posts = sorted(posts, key=lambda x: x['delete_time'], reverse=True)  
    for post in posts:
        delay = parse(post['delete_time']) - now
        total_sec = delay.total_seconds()
        time.sleep(total_sec)
        if total_sec>=0:
			if 'TG' in post.get('platform'):		
                try:
                    delete_post_in_tg(post['id'])
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



