from telebot import TeleBot
from dotenv import load_dotenv
import os
import logging
import datetime
from models import User, Rool, Report, ChatUser

load_dotenv()

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# مقداردهی API_KEY و ساخت بات
API_KEY = os.getenv('API_KEY')
bot = TeleBot(API_KEY)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    ChatUser.get_or_create(chat_id=chat_id)
    bot.send_message(chat_id, '👋 خوش آمدید! لطفا /register را برای ثبت‌نام بزنید.\nبرای مشاهده دستورات /help را وارد کنید.')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, '📜 **راهنمای دستورات:**\n'
                                     '/start - شروع\n'
                                     '/register - ثبت‌نام\n'
                                     '/show_users - نمایش کاربران (فقط برای مستر)\n'
                                     '/delete_user - حذف کاربر (فقط مستر)\n'
                                     '/send_report - ارسال گزارش\n'
                                     '/show_reports - مشاهده گزارش‌ها\n'
                                     '/edit_report - ویرایش گزارش\n'
                                     '/delete_report - حذف گزارش\n'
                                     '/alert - ارسال هشدار\n'
                                     '/help - راهنما')

@bot.message_handler(commands=['register'])
def set_first_name(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    bot.send_message(chat_id, '✍ لطفا **نام** خود را وارد کنید:')
    bot.register_next_step_handler_by_chat_id(chat_id, set_last_name)

def set_last_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['first_name'] = message.text
    bot.send_message(chat_id, '✍ لطفا **نام خانوادگی** خود را وارد کنید:')
    bot.register_next_step_handler_by_chat_id(chat_id, set_phone)

def set_phone(message):
    chat_id = message.chat.id
    user_data[chat_id]['last_name'] = message.text
    bot.send_message(chat_id, '📞 لطفا **شماره تماس** خود را وارد کنید:')
    bot.register_next_step_handler_by_chat_id(chat_id, set_role)

def set_role(message):
    chat_id = message.chat.id
    user_data[chat_id]['phone'] = message.text

    master_exists = User.select().join(Rool).where(Rool.name == 'مستر').exists()
    bot.send_message(chat_id, '🔰 لطفا **نقش خود را انتخاب کنید:**')
    
    if master_exists:
        bot.send_message(chat_id, '❌ **نقش "مستر" قبلاً ثبت شده است!** لطفا نقش دیگری انتخاب کنید.')

    bot.send_message(chat_id, '1️⃣ - مستر' if not master_exists else '')
    bot.send_message(chat_id, '2️⃣ - عادی')
    bot.register_next_step_handler_by_chat_id(chat_id, set_status_work, master_exists)

def set_status_work(message, master_exists):
    chat_id = message.chat.id
    role_choice = message.text.strip()

    if role_choice == '1' and master_exists:
        bot.send_message(chat_id, '❌ **نقش "مستر" در دسترس نیست. لطفاً مجدداً /register را وارد کنید.**')
        return

    user_data[chat_id]['rool'] = 'مستر' if role_choice == '1' else 'عادی'

    bot.send_message(chat_id, '💼 **وضعیت شغلی خود را انتخاب کنید:**\n1️⃣ - شاغل\n2️⃣ - بیکار')
    bot.register_next_step_handler_by_chat_id(chat_id, finish_register)

def finish_register(message):
    chat_id = message.chat.id
    status_choice = message.text.strip()
    user_data[chat_id]['status_work'] = 'شاغل' if status_choice == '1' else 'بیکار'

    rool, _ = Rool.get_or_create(name=user_data[chat_id]['rool'])
    User.create(
        chat_id=chat_id,
        first_name=user_data[chat_id]['first_name'],
        last_name=user_data[chat_id]['last_name'],
        phone=user_data[chat_id]['phone'],
        rool=rool,
        status_work=user_data[chat_id]['status_work']
    )

    bot.send_message(chat_id, '✅ **ثبت‌نام شما با موفقیت انجام شد!**')
    del user_data[chat_id]

@bot.message_handler(commands=['show_users'])
def show_users(message):
    chat_id = message.chat.id
    user = User.get_or_none(User.chat_id == chat_id)

    if user and user.rool.name == 'مستر':
        users = User.select()
        for u in users:
            bot.send_message(chat_id, f'👤 {u.first_name} {u.last_name} | 📞 {u.phone} | 🔰 {u.rool.name}')
    else:
        bot.send_message(chat_id, "❌ **شما مجاز به مشاهده‌ی کاربران نیستید.**")

@bot.message_handler(commands=['delete_user'])
def delete_user(message):
    chat_id = message.chat.id
    is_master = User.select().join(Rool).where(Rool.name == 'مستر', User.chat_id == chat_id).exists()

    if is_master:
        bot.send_message(chat_id, '📞 لطفا شماره کاربر را وارد کنید:')
        bot.register_next_step_handler_by_chat_id(chat_id, confirm_delete_user)
    else:
        bot.send_message(chat_id, '❌ **شما مجاز به حذف کاربران نیستید.**')

def confirm_delete_user(message):
    chat_id = message.chat.id
    user = User.get_or_none(User.phone == message.text)

    if user:
        user.delete_instance()
        bot.send_message(chat_id, '✅ **کاربر حذف شد.**')
    else:
        bot.send_message(chat_id, '❌ **کاربری با این شماره یافت نشد.**')

@bot.message_handler(commands=['send_report'])
def send_report(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, '📝 لطفا متن گزارش را وارد کنید:')
    bot.register_next_step_handler_by_chat_id(chat_id, save_report)

def save_report(message):
    chat_id = message.chat.id
    user = User.get_or_none(User.chat_id == chat_id)

    if user:
        Report.create(user=user, date=datetime.datetime.now(), text=message.text)
        bot.send_message(chat_id, '✅ **گزارش شما ثبت شد.**')
    else:
        bot.send_message(chat_id, '❌ **لطفا ابتدا ثبت‌نام کنید.**')

