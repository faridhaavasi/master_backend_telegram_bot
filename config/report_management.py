from telebot import TeleBot
from models import User, Report
import datetime

def report_handlers(bot: TeleBot):
    @bot.message_handler(commands=['send_report'])
    def send_report(message):
        chat_id = message.chat.id
        bot.send_message(chat_id, 'لطفا متن گزارش خود را وارد کنید:')
        bot.register_next_step_handler(message, save_report)

    def save_report(message):
        chat_id = message.chat.id
        user = User.get_or_none(User.chat_id == chat_id)
        if user:
            Report.create(user=user, date=datetime.datetime.now(), text=message.text).save()
            bot.send_message(chat_id, '✅ گزارش شما با موفقیت ثبت شد!')
        else:
            bot.send_message(chat_id, "❌ ابتدا ثبت‌نام کنید.")

    @bot.message_handler(commands=['show_reports'])
    def show_reports(message):
        chat_id = message.chat.id
        reports = Report.select()
        for r in reports:
            bot.send_message(chat_id, f'📅 تاریخ: {r.date}\n📄 متن گزارش: {r.text}')
