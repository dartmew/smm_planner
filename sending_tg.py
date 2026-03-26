import telebot
import time

def sending_img_in_tg(pending):
	token = env.str('POSTING_TELEGRAM_BOT_API_KEY')
	chat_id = env.str('TELEGRAM_CHAT_ID')
	bot = telebot.TeleBot(token=token)
	for post in pending:	
		bot.send_photo(chat_id=chat_id, photo=post['media_like'], caption=post['name']) 
		time.sleep(2)
	
		
	
	

