from celery import Celery
import telebot
import os

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

celery_app = Celery('tasks', broker='pyamqp://guest@rabbitmq:5672//', backend='rpc://')

@celery_app.task
def send_alert_task():
    from models import ChatUser  # برای جلوگیری از import loop
    for user in ChatUser.select():
        bot.send_message(user.chat_id, '⚠️ توجه کن!')
        bot.send_message(user.chat_id, 'این یک پیام تستی است.')