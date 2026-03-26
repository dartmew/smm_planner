import requests
import hashlib
import random
import time

# Ваш ID приложения, секретный ключ приложения и токен доступа
app_id = '512004455067'
app_secret_key = 'F3CB96135A48059A49897505'
access_token = '-n-omXmMzNv318yDyjiWNQkQZ8JNCzjtWnv80uSUIzF0u1V1YYFbjECVhKHnvAynMxsW7vL4ebIld7b4Vnfi'

# ID группы, в которой будет публиковаться сообщение
group_id = '70000048710396'

# Текст сообщения
message = 'Hello, World!'

# Формирование параметров запроса
params = {
    'application_key': app_id,
    'method': 'mediatopic.post',
    'gid': group_id,
    'type': 'GROUP_THEME',
    'format': 'json',
    'media': [{"type": "text", "text": message}, {"type": "photo", "list": [{ "id": "1234567890"}]}]
}

# Формирование подписи запроса
signature_data = ''.join([f'{k}={v}' for k, v in sorted(params.items())])
signature_data += app_secret_key

# Добавление подписи и токена доступа к параметрам запроса
params['sig'] = hashlib.md5(signature_data.encode('utf-8')).hexdigest()
params['access_token'] = access_token

# Отправка запроса
response = requests.post('https://api.ok.ru/fb.do', params=params)

# Проверка ответа
if response.status_code == 200:
    print('Сообщение успешно опубликовано!')
else:
    print(f'Ошибка публикации: {response.json()}')