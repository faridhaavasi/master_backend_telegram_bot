from telebot import TeleBot
from dotenv import load_dotenv
import os
from models import User , Rool
load_dotenv()

API_KEY = os.getenv('API_KEY')

bot = TeleBot(API_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hello, I am a bot that can help you with your tasks. What is your name?')




bot.polling()
