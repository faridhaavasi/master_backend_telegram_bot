from telebot import TeleBot
from dotenv import load_dotenv
import os
from models import db
load_dotenv()

API_KEY = os.getenv('API_KEY')

bot = TeleBot(API_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    db.connect()
    bot.reply_to(message, 'Hello, welcome to the bot!')

bot.polling()
