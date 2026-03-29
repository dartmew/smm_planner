# import requests
# import hashlib
# from environs import Env


# def upload_foto_and_get_id(group_id, app_id, access_token, app_secret_key, img_url):
#     upload_url_params = {
#         'application_key': app_id,
#         'method': 'photos.getUploadUrl',
#         'gid': group_id,
#         'format': 'json'
#     }
#     signature_data = ''.join([f'{k}={v}' for k, v in sorted(upload_url_params.items())])
#     signature_data += app_secret_key
#     upload_url_params['sig'] = hashlib.md5(signature_data.encode('utf-8')).hexdigest()
#     upload_url_params['access_token'] = access_token
#     response = requests.post('https://api.ok.ru/fb.do', data=upload_url_params).json()
#     upload_url = response['upload_url']
#     photo =
#     upload_response = requests.post(upload_url, files=photo).json()
#     photo_id = upload_response['photo_id']
#     return photo_id


# def publish_post_ok(pending):
#     env = Env()
#     env.read_env()
#     app_id = env.str('OK_APP_ID')
#     app_secret_key = env.str('OK_APP_SECRET_KEY')
#     access_token = env.str('OK_ACCESS_TOKEN')
#     group_id = env.str('OK_GROUP_ID')
#     message = pending.get('text')
#     img_url = pending.get('media_link')
#     photo_id = upload_foto_and_get_id(
#         group_id,
#         app_id,
#         access_token,
#         app_secret_key,
#         img_url
#     )
#     params = {
#         'application_key': app_id,
#         'method': 'mediatopic.post',
#         'gid': group_id,
#         'type': 'GROUP_THEME',
#         "text": message,
#         'format': 'json',
#         'attachment': {
#             'media': [
#                 {"type": "photo", "list": [{"id": photo_id}]},
#             ]
#         }
#     }
#     signature_data = ''.join([f'{k}={v}' for k, v in sorted(params.items())])
#     signature_data += app_secret_key
#     params['sig'] = hashlib.md5(signature_data.encode('utf-8')).hexdigest()
#     params['access_token'] = access_token
#     response = requests.post('https://api.ok.ru/fb.do', params=params)
#     if response.status_code == 200:
#         return True
#     else:
#         return False
