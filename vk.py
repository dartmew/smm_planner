import json
from pathlib import Path

from decouple import config
import requests

import sheets_api

VK_API_VERSION = '5.199'
VK_ACCESS_TOKEN = config('VK_ACCESS_TOKEN')
VK_GROUP_ID = int(config('VK_GROUP_ID'))
VK_URL = 'https://api.vk.ru/method'
spreadsheet_id = config('SPREADSHEET_ID')
client = sheets_api.get_client()


# отправить в ВК
def send_to_vk(post):
    # получение адреса сервера ВК для загрузки изображения
    params = {
        'access_token': VK_ACCESS_TOKEN,
        'group_id': VK_GROUP_ID,
        'v': VK_API_VERSION
    }
    upload_server = requests.get(f'{VK_URL}/photos.getWallUploadServer', params=params)
    upload_server.raise_for_status()
    print('получение адреса сервера ВК для загрузки изображения:', upload_server.json())

    # загрузить в память файлы для публикации
    media_files = sheets_api.download_drive_files_to_memory(post['media_link'])
    print('загружены в память файлы:', media_files)
    attachments = []
    for number, media_file in enumerate(media_files, 1):
        # загрузка изображения на сервер ВК
        upload_url = upload_server.json()['response']['upload_url']
        uploaded_image = requests.post(upload_url, files={'photo': (f'{number}.png', media_file)})
        uploaded_image.raise_for_status()
        print('загрузка изображения на сервер ВК:', uploaded_image.json())

        # сохранение изображения в альбоме группы
        params = {
            'access_token': VK_ACCESS_TOKEN,
            'group_id': VK_GROUP_ID,
            'server': uploaded_image.json()['server'],
            'photo': uploaded_image.json()['photo'],
            'hash': uploaded_image.json()['hash'],
            'v': VK_API_VERSION
        }
        saved_image = requests.post(f'{VK_URL}/photos.saveWallPhoto', params=params)
        saved_image.raise_for_status()
        print('сохранение изображения в альбоме группы:', saved_image.json())

        saved_image = saved_image.json()['response'][0]
        print('получение аттачмента:', saved_image)
        attachment = f'photo{saved_image["owner_id"]}_{saved_image["id"]}'
        attachments.append(attachment)
        print('получение аттачментов:', attachments)

    # публикация изображений на стене группы
    params = {
        'access_token': VK_ACCESS_TOKEN,
        'owner_id': -VK_GROUP_ID,
        'from_group': 1,
        'attachments': (",".join(attachments)),
        'primary_attachments_mode': 'grid',
        'message': post['text'],
        'v': VK_API_VERSION
    }
    published_post = requests.post(f'{VK_URL}/wall.post', params=params)
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
        if 'vk' in ids:
            ids['vk'][post_id] = vk_post_id
        else:
            ids['vk'] = {post_id: vk_post_id}
        json.dump(ids, open('posts_ids.json', 'w+'))


# удалить пост
def delete_post(post_id: str):
    with open('posts_ids.json', 'r+') as file:
        ids = json.load(file)
        id_for_delete = ids['vk'][post_id]
        params = {
            'access_token': VK_ACCESS_TOKEN,
            'owner_id': -VK_GROUP_ID,
            'post_id': id_for_delete,
            'v': VK_API_VERSION
        }
        result = requests.post(f'{VK_URL}/wall.delete', params=params)
        result.raise_for_status()
        if result:
            del ids['vk'][post_id]
            json.dump(ids, open('posts_ids.json', 'w+'))


if __name__ == '__main__':
    post = get_pending_post()
    print('пост из таблицы получен:', post)
    send_to_vk(post)
