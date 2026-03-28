import telebot
import time
import json
from dotenv import load_dotenv
from environs import env

load_dotenv()
TOKEN = env.str('POSTING_TELEGRAM_BOT_API_KEY')
CHAT_ID = env.str('TELEGRAM_CHAT_ID')


def sending_post_in_tg(posts):
	bot = telebot.TeleBot(token=TOKEN)
	for post in posts:
		send = bot.send_photo(chat_id=CHAT_ID, photo='https://avatars.mds.yandex.net/i?id=d3c260a598a0f42a73eb0c9a62df928d_l-4517378-images-thumbs&n=13', caption=post['TEXT'])
		with open('posts_ids.json', 'r+') as file:
			ids = json.load(file)
			ids[post['ID']]=send.message_id
			json.dump(ids, open('posts_ids.json','w+'))
		time.sleep(2)


def delete_post_in_tg(post_id):
	bot = telebot.TeleBot(token=TOKEN)  
	with open('posts_ids.json', 'r+') as file:
		ids = json.load(file)
		id_for_delete = ids[post_id]
		result = bot.delete_messages(
			chat_id=CHAT_ID,  
			message_ids=[id_for_delete]
		)
		if result:
			del ids[post_id]
			json.dump(ids, open('posts_ids.json','w+'))
    


