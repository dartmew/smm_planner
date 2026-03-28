import json
from pathlib import Path
import re

from google_drive_id_extractor import extract_google_drive_id
from decouple import config
import requests

import sheets_api

API_VERSION = '5.199'
ACCESS_TOKEN = config('VK_ACCESS_TOKEN')
GROUP_ID = int(config('VK_GROUP_ID'))
spreadsheet_id = config('SPREADSHEET_ID')
client = sheets_api.get_client()


# отправить в ВК
def send_to_vk():
    post = get_pending_post()
    print('пост из таблицы получен:', post)

    # скачать картинку для публикации
    file_id = extract_google_drive_id(post['media_link'])
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    image_path = download_image(url)
    print('картинка скачана:', image_path)

    # получение адреса сервера ВК для загрузки изображения
    params = {
        'access_token': ACCESS_TOKEN,
        'group_id': GROUP_ID,
        'v': API_VERSION
    }
    upload_server = requests.get('https://api.vk.ru/method/photos.getWallUploadServer', params=params)
    upload_server.raise_for_status()
    print('получение адреса сервера ВК для загрузки изображения:', upload_server.json())

    # загрузка изображения на сервер ВК
    upload_url = upload_server.json()['response']['upload_url']
    with open(image_path, 'rb') as file:
        files = {
            'photo': file,
        }
        uploaded_image = requests.post(upload_url, files=files)
        uploaded_image.raise_for_status()
    print('загрузка изображения на сервер ВК:', uploaded_image.json())

    # сохранение изображения в альбоме группы
    params = {
        'access_token': ACCESS_TOKEN,
        'group_id': GROUP_ID,
        'server': uploaded_image.json()['server'],
        'photo': uploaded_image.json()['photo'],
        'hash': uploaded_image.json()['hash'],
        'v': API_VERSION
    }
    saved_image = requests.post('https://api.vk.ru/method/photos.saveWallPhoto', params=params)
    saved_image.raise_for_status()
    print('сохранение изображения в альбоме группы:', saved_image.json())

    # публикация изображения на стене группы
    saved_image = saved_image.json()['response'][0]
    print('получение аттачмента:', saved_image)
    attachment = f'photo{saved_image["owner_id"]}_{saved_image["id"]}'
    print('получение аттачмента:', attachment)
    params = {
        'access_token': ACCESS_TOKEN,
        'owner_id': -GROUP_ID,
        'from_group': 1,
        'attachments': [attachment],
        'message': post['text'],
        'v': API_VERSION
    }
    published_post = requests.post('https://api.vk.ru/method/wall.post', params=params)
    published_post.raise_for_status()
    print('публикация изображения на стене группы:', published_post.json())

    if published_post.json():
        save_post_id(post['id'], published_post.json()['response']['post_id'])
        print('сохранение в файл id поста:', published_post.json()['response']['post_id'])
        sheets_api.update_post_status(
            client,
            spreadsheet_id,
            post['row'],
            sheets_api.STATUS_PUBLISHED)
        print('обновление статуса в таблице')
    else:
        sheets_api.update_post_error(client, spreadsheet_id, post['row'], "ошибка")


# для теста пока что: скачивание картинки по ссылке гугл диска
def download_image(image_url):
    response = requests.get(image_url, headers={'User-Agent': 'Mozilla/5.0 (compatible; HandsomeBrowser/1.2)'})
    response.raise_for_status()
    content_disposition = response.headers.get('content-disposition')
    file_name = re.search(r'filename="([^"]+)"', content_disposition)
    if file_name:
        download_path = file_name.group(1)
    else:
        download_path = 'downloaded.jpg'
    image = Path(download_path)
    image.write_bytes(response.content)
    return download_path


# для теста пока что: взять 1 пост для публикации
def get_pending_post():
    records = sheets_api.get_all_records(client, spreadsheet_id)
    posts = sheets_api.filter_posts_by_status(records, sheets_api.STATUS_PENDING)
    return posts[0]


# запомнить ИД поста в json файл
def save_post_id(post_id, vk_post_id):
    file_path = Path("posts_ids.json")
    if not file_path.exists():
        file_path.touch()
        file_path.write_text('{}')

    with open('posts_ids.json', 'r+') as file:
        ids = json.load(file)
        ids[post_id] = vk_post_id
        json.dump(ids, open('posts_ids.json', 'w+'))


# удалить пост
def delete_post(post_id: str):
    with open('posts_ids.json', 'r+') as file:
        ids = json.load(file)
        id_for_delete = ids[post_id]
        params = {
            'access_token': ACCESS_TOKEN,
            'owner_id': -GROUP_ID,
            'post_id': id_for_delete,
            'v': API_VERSION
        }
        result = requests.post('https://api.vk.ru/method/wall.delete', params=params)
        result.raise_for_status()
        if result:
            del ids[post_id]
