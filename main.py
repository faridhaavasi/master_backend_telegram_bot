from telebot import TeleBot
from telebot import logger
from dotenv import load_dotenv
import os
import logging
from models import User , Rool


load_dotenv()

logger.setLevel(logging.WARNING)
API_KEY = os.getenv('API_KEY')

bot = TeleBot(API_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'خوش آمدید لطفا /register را بزنید')


@bot.message_handler(commands=['register'])
def set_first_name(message, first_name=None):
    bot.send_message(message.chat.id, 'لطفا نام خود را وارد کنید')
    bot.register_next_step_handler(message, callback=set_last_name, first_name=message.text)

def set_last_name(message, first_name):
    bot.send_message(message.chat.id, 'لطفا نام خانوادگی خود را وارد کنید')
    bot.register_next_step_handler(message, callback=set_phone, first_name=first_name, last_name=message.text)

def set_phone(message, first_name, last_name):
    bot.send_message(message.chat.id, 'لطفا شماره تماس خود را وارد کنید')
    bot.register_next_step_handler(message, callback=set_rool, first_name=first_name, 
                                   last_name=last_name, 
                                   phone=message.text)

def set_rool(message, first_name, last_name, phone):
    bot.send_message(message.chat.id, 'لطفا نقش خود را انتخاب کنید')
    bot.send_message(message.chat.id, '1- مستر')
    bot.send_message(message.chat.id, '2- عادی')
    bot.register_next_step_handler(message, callback=set_status_work, first_name=first_name,
                                   last_name=last_name, phone=phone, rool=message.text)


def set_status_work(message, first_name, last_name, phone, rool):
    bot.send_message(message.chat.id, 'لطفا وضعیت کاری خود را انتخاب کنید')
    bot.send_message(message.chat.id, '1-شاغل')
    bot.send_message(message.chat.id, '2- بیکار')
    bot.register_next_step_handler(message, callback=finish_register, first_name=first_name,
                                   last_name=last_name, phone=phone, rool=rool, status_work=message.text)


def finish_register(message, first_name, last_name, phone, rool, status_work):
    rool, _ = Rool.get_or_create(name=rool)  # جلوگیری از ایجاد نقش‌های تکراری
    user = User.create(
        chat_id=message.chat.id,  # ذخیره chat_id
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        rool=rool,
        status_work=str(status_work)
    )
    user.save()

    bot.send_message(message.chat.id, 'ثبت نام شما با موفقیت انجام شد')
@bot.message_handler(commands=['show_users'])
def show_users(message):
    logger.info(f'User with chat_id {message.chat.id} requested to show users')

    user = User.get_or_none(User.chat_id == message.chat.id)  

    if user is None:
        bot.send_message(message.chat.id, "❌ کاربری با این ID یافت نشد، لطفا ثبت‌نام کنید.")
        return  # جلوگیری از اجرای ادامه‌ی تابع

    if user.rool.name == 'مستر':
        users = User.select()
        for u in users:
            bot.send_message(
                message.chat.id, 
                f'👤 نام: {u.first_name}\n'
                f'📛 نام خانوادگی: {u.last_name}\n'
                f'📞 شماره تماس: {u.phone}\n'
                f'🔰 نقش: {u.rool.name}\n'
                f'💼 وضعیت کاری: {u.status_work}'
            )
    else:
        bot.send_message(message.chat.id, "❌ شما مجاز به مشاهده‌ی کاربران نیستید.")




bot.polling()
