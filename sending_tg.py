import telebot
import json
from dotenv import load_dotenv
from environs import Env
from google_drive_id_extractor import extract_google_drive_id
from text_formatter import format_text

env = Env()
load_dotenv()
TOKEN = env.str('POSTING_TELEGRAM_BOT_API_KEY')
CHAT_ID = env.str('TELEGRAM_CHAT_ID')


def sending_post_in_tg(post):
    bot = telebot.TeleBot(token=TOKEN)
    send = bot.send_photo(
        chat_id=CHAT_ID,
        photo=f'''https://drive.google.com/uc?export
        =download&id={extract_google_drive_id(post['media_link'])}''',
        caption=format_text(post['text']))
    with open('posts_ids.json', 'r+') as file:
        ids = json.load(file)
        ids[post['id']] = send.message_id
        json.dump(ids, open('posts_ids.json', 'w+'))


def delete_post_in_tg(post_id):
    post_id = str(post_id)
    bot = telebot.TeleBot(token=TOKEN)
    with open('posts_ids.json', 'r+') as file:
        ids = json.load(file)
        id_for_delete = ids[post_id]
        result = bot.delete_messages(
            chat_id=CHAT_ID,
            message_ids=[id_for_delete])
        if result:
            del ids[post_id]
            with open('posts_ids.json', 'w+') as file:
                json.dump(ids, file)
