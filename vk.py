import json
from pathlib import Path

from decouple import config
import requests

from sheets_api import download_drive_files_to_memory

VK_API_VERSION = '5.199'
VK_ACCESS_TOKEN = config('VK_ACCESS_TOKEN')
VK_GROUP_ID = int(config('VK_GROUP_ID'))
VK_URL = 'https://api.vk.ru/method'


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

    # загрузить в память файлы для публикации
    media_files = download_drive_files_to_memory(post['media_link'])
    print('загружены в память файлы:', media_files)
    attachments = []
    for number, media_file in enumerate(media_files, 1):
        # загрузка изображения на сервер ВК
        upload_url = upload_server.json()['response']['upload_url']
        uploaded_image = requests.post(
            upload_url,
            files={'photo': (f'{number}.png', media_file)}
        )
        uploaded_image.raise_for_status()

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
        # сборка аттачментов для запроса на публикацию (след.шаг)
        saved_image = saved_image.json()['response'][0]
        attachment = f'photo{saved_image["owner_id"]}_{saved_image["id"]}'
        attachments.append(attachment)

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

    if published_post.json():
        _save_post_id(post['id'], published_post.json()['response']['post_id'])


# запомнить ИД поста в json файл
def _save_post_id(post_id, vk_post_id):
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
