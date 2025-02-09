from telebot import TeleBot
from dotenv import load_dotenv
import os
from config.user_management import register_handlers
from config.report_management import report_handlers
from config.alert_management import alert_handlers

load_dotenv()

API_KEY = os.getenv('API_KEY')
bot = TeleBot(API_KEY)

register_handlers(bot)
report_handlers(bot)
alert_handlers(bot)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'خوش آمدید لطفا /register را بزنید')
    bot.send_message(message.chat.id, 'برای مشاهده دستورات /help را بزنید')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'راهنمای دستورات:\n'
                                     '/start - شروع\n'
                                     '/register - ثبت‌نام\n'
                                     '/show_users - نمایش کاربران (فقط مستر)\n'
                                     '/delete_user - حذف کاربر (فقط مستر)\n'
                                     '/send_report - ارسال گزارش\n'
                                     '/show_reports - نمایش گزارش‌ها\n'
                                     '/edit_report - ویرایش گزارش\n'
                                     '/delete_report - حذف گزارش\n'
                                     '/alert - ارسال هشدار (Celery)\n'
                                     '/help - راهنما')

