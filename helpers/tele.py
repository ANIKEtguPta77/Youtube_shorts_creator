import sys
import requests
# import telegram
from telegram import Bot

class TeleGramClient:
    def __init__(self):
        self.TOKEN = "7302198831:AAFtfRrLRdPn94fLTb1GsNFQqXVInpD-Wsg" 
        
    def send_telegram_message(self, chat_id, message):
        bot = Bot(token=self.TOKEN)
        print(bot)
        try:
            print(chat_id,message)
            bot.sendMessage(chat_id=chat_id, text=message)
            print(f"Message sent to chat_id: {chat_id}")
        except Exception as e:
            print(f"Error sending message to chat_id {chat_id}: {e}")
        
    def send_telegram_video(self, chat_id, video_file_path):
        bot = Bot(token=self.TOKEN)
        try:
            bot.send_video(chat_id=chat_id, video=open(video_file_path, 'rb'))
            print(f"Video sent to chat_id: {chat_id}")
        except Exception as e:
            print(f"Error sending video to chat_id {chat_id}: {e}") 