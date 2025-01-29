import telebot
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# create a database
conn = sqlite3.connect('sqlite3.db', check_same_thread=False)
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
    bot.send_message(message.chat.id, "  بیکار هستید یا شاغل لطفاً وضعیت خود را وارد کنید:")
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

bot.polling()
