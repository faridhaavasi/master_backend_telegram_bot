from celery_app import app
from models import User
from telebot import TeleBot
import os

API_KEY = os.getenv('API_KEY')
bot = TeleBot(API_KEY)

@app.task
def send_alert_task(chat_id):
    bot.send_message(chat_id, '⚠️ هشدار جدید دریافت شد!')
