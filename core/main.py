import telebot
import sqlite3
import os
from dotenv import load_dotenv
from telebot import types

load_dotenv()

# create a database
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    firstname TEXT,
    lastname TEXT,
    phone TEXT,
    status TEXT, 
    rool TEXT DEFAULT 'user'
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS reports (
    userid INTEGER,
    report TEXT
)
''')
conn.commit()

# read token from file
API_TOKEN = os.getenv('API_TOKEN')
if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set or is empty!")

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "لطفاً نام خود را وارد کنید:")
    bot.register_next_step_handler(message, get_first_name)

def get_first_name(message):
    firstname = message.text
    bot.send_message(message.chat.id, "لطفاً نام خانوادگی خود را وارد کنید:")
    bot.register_next_step_handler(message, get_last_name, firstname)

def get_last_name(message, firstname):
    lastname = message.text
    bot.send_message(message.chat.id, "لطفاً شماره تلفن خود را وارد کنید:")
    bot.register_next_step_handler(message, get_phone, firstname, lastname)

def get_phone(message, firstname, lastname):
    phone = message.text
    bot.send_message(message.chat.id, "لطفاً وضعیت خود را وارد کنید:")
    bot.register_next_step_handler(message, get_role, firstname, lastname, phone)

def get_role(message, firstname, lastname, phone):
    status = message.text
    bot.send_message(message.chat.id, "لطفاً نقش خود را انتخاب کنید (عادی یا مستر):")
    bot.register_next_step_handler(message, save_user, firstname, lastname, phone, status)

def save_user(message, firstname, lastname, phone, status):
    rool = message.text.lower()
    if rool not in ['عادی', 'مستر']:
        bot.send_message(message.chat.id, "نقش نامعتبر است. لطفاً دوباره تلاش کنید.")
        return
    
    cursor.execute("INSERT INTO users (firstname, lastname, phone, status, rool) VALUES (?, ?, ?, ?, ?)",
                   (firstname, lastname, phone, status, rool))
    conn.commit()
    bot.send_message(message.chat.id, "اطلاعات شما با موفقیت ذخیره شد!")

@bot.message_handler(commands=['report'])
def report(message):
    # ایجاد دکمه برای ارسال گزارش
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('ارسال گزارش')
    bot.send_message(message.chat.id, "برای ارسال گزارش، دکمه زیر را فشار دهید:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'ارسال گزارش')
def receive_report(message):
    bot.send_message(message.chat.id, "لطفاً متن گزارش خود را وارد کنید:")
    bot.register_next_step_handler(message, save_report)

def save_report(message):
    report_text = message.text
    user_id = message.from_user.id  # شناسه کاربر که باید در پایگاه داده ذخیره 
    cursor.execute("INSERT INTO reports (userid, report) VALUES (?, ?)", (user_id, report_text))
    conn.commit()
    bot.send_message(message.chat.id, "گزارش شما با موفقیت ذخیره شد!")

bot.polling()
