import telebot
import sqlite3
import os
from dotenv import load_dotenv
from telebot import types
import schedule
import time
import threading

load_dotenv()

# create a database connection to a SQLite database
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    userid INTEGER PRIMARY KEY,
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
    report TEXT,
    report_date DATE DEFAULT CURRENT_DATE
)
''')
conn.commit()

# Get the bot token from the environment
API_TOKEN = os.getenv('API_TOKEN')
if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set or is empty!")

bot = telebot.TeleBot(API_TOKEN)

def check_reports():
    today = time.strftime("%Y-%m-%d")
    cursor.execute("SELECT userid FROM users WHERE rool = 'عادی'")
    users = cursor.fetchall()
    for user in users:
        user_id = user[0]
        cursor.execute("SELECT * FROM reports WHERE userid = ? AND report_date = ?", (user_id, today))
        if not cursor.fetchone():
            bot.send_message(user_id, "لطفاً گزارش روزانه خود را ارسال کنید.")

def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Schedule the check_reports function to run every day at a specific time
schedule.every().day.at("09:00").do(check_reports)

# Start the schedule checker in a separate thread
threading.Thread(target=schedule_checker).start()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE userid = ?", (user_id,))
    if cursor.fetchone():
        bot.send_message(message.chat.id, "شما قبلاً ثبت‌نام کرده‌اید!")
    else:
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
    if not phone.isdigit() or len(phone) != 11:
        bot.send_message(message.chat.id, "شماره تلفن نامعتبر است. لطفاً یک شماره ۱۱ رقمی وارد کنید.")
        bot.register_next_step_handler(message, get_phone, firstname, lastname)
    else:
        bot.send_message(message.chat.id, "لطفاً وضعیت خود را وارد کنید:")
        bot.register_next_step_handler(message, get_status, firstname, lastname, phone)

def get_status(message, firstname, lastname, phone):
    status = message.text
    bot.send_message(message.chat.id, "لطفاً نقش خود را انتخاب کنید (عادی یا مستر):")
    bot.register_next_step_handler(message, save_user, firstname, lastname, phone, status)

def save_user(message, firstname, lastname, phone, status):
    rool = message.text.lower()
    if rool not in ['عادی', 'مستر']:
        bot.send_message(message.chat.id, "نقش نامعتبر است. لطفاً دوباره تلاش کنید.")
        return
    
    user_id = message.from_user.id
    cursor.execute("INSERT INTO users (userid, firstname, lastname, phone, status, rool) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, firstname, lastname, phone, status, rool))
    conn.commit()
    bot.send_message(message.chat.id, "اطلاعات شما با موفقیت ذخیره شد!")

@bot.message_handler(commands=['report'])
def report(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add('ارسال گزارش')
    bot.send_message(message.chat.id, "برای ارسال گزارش، دکمه زیر را فشار دهید:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'ارسال گزارش')
def receive_report(message):
    bot.send_message(message.chat.id, "لطفاً متن گزارش خود را وارد کنید:")
    bot.register_next_step_handler(message, save_report)

def save_report(message):
    report_text = message.text
    user_id = message.from_user.id
    cursor.execute("INSERT INTO reports (userid, report) VALUES (?, ?)", (user_id, report_text))
    conn.commit()
    bot.send_message(message.chat.id, "گزارش شما با موفقیت ذخیره شد!")

@bot.message_handler(commands=['users'])
def list_users(message):
    user_id = message.from_user.id
    # Get the role of the user
    cursor.execute("SELECT rool FROM users WHERE userid = ?", (user_id,))
    user_role = cursor.fetchone()
    
    if user_role and user_role[0] == 'مستر':
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        if users:
            response = "لیست کاربران:\n"
            for user in users:
                response += f"نام: {user[1]} {user[2]}, تلفن: {user[3]}, وضعیت: {user[4]}, نقش: {user[5]}\n"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "هیچ کاربری ثبت‌نام نکرده است.")
    else:
        bot.send_message(message.chat.id, "شما دسترسی لازم برای مشاهده لیست کاربران را ندارید!")

bot.polling()