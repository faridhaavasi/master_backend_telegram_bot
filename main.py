from telebot import TeleBot
from telebot import logger
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

from models import User, Rool, Report

load_dotenv()

logger.setLevel(logging.INFO)
API_KEY = os.getenv('API_KEY')

bot = TeleBot(API_KEY)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, ' خوش آمدید لطفا /register را بزنید   و برای راهنمایی /help'  )
@bot.message_handler(commands=['register'])
def set_first_name(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}  

    bot.send_message(chat_id, 'لطفا نام خود را وارد کنید')
    bot.register_next_step_handler(message, set_last_name)

def set_last_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['first_name'] = message.text  

    bot.send_message(chat_id, 'لطفا نام خانوادگی خود را وارد کنید')
    bot.register_next_step_handler(message, set_phone)

def set_phone(message):
    chat_id = message.chat.id
    user_data[chat_id]['last_name'] = message.text  

    bot.send_message(chat_id, 'لطفا شماره تماس خود را وارد کنید')
    bot.register_next_step_handler(message, set_rool)

def set_rool(message):
    chat_id = message.chat.id
    user_data[chat_id]['phone'] = message.text  

    master_exists = User.select().join(Rool).where(Rool.name == 'مستر').exists()

    bot.send_message(chat_id, 'لطفا نقش خود را انتخاب کنید:')
    
    if master_exists:
        bot.send_message(chat_id, '❌ نقش "مستر" قبلاً ثبت شده است. لطفا نقش دیگری را انتخاب کنید.')
    else:
        bot.send_message(chat_id, '1- مستر')
    
    bot.send_message(chat_id, '2- عادی')
    bot.register_next_step_handler(message, set_status_work, master_exists)

def set_status_work(message, master_exists):
    chat_id = message.chat.id
    role_choice = message.text.strip()

    if role_choice == '1' and master_exists:
        bot.send_message(chat_id, '❌ شما نمی‌توانید به عنوان "مستر" ثبت نام کنید. لطفا مجددا /register را بزنید و نقش دیگری انتخاب کنید.')
        return

    if role_choice == '1':
        user_data[chat_id]['rool'] = 'مستر'
    elif role_choice == '2':
        user_data[chat_id]['rool'] = 'عادی'
    else:
        bot.send_message(chat_id, '❌ نقش نامعتبر! لطفا مجددا /register را بزنید')
        return

    bot.send_message(chat_id, 'لطفا وضعیت کاری خود را انتخاب کنید:')
    bot.send_message(chat_id, '1- شاغل')
    bot.send_message(chat_id, '2- بیکار')
    bot.register_next_step_handler(message, finish_register)

def finish_register(message):
    chat_id = message.chat.id
    status_choice = message.text.strip()

    if status_choice == '1':
        user_data[chat_id]['status_work'] = 'شاغل'
    elif status_choice == '2':
        user_data[chat_id]['status_work'] = 'بیکار'
    else:
        bot.send_message(chat_id, '❌ وضعیت کاری نامعتبر! لطفا مجددا /register را بزنید')
        return

    first_name = user_data[chat_id]['first_name']
    last_name = user_data[chat_id]['last_name']
    phone = user_data[chat_id]['phone']
    rool_name = user_data[chat_id]['rool']
    status_work = user_data[chat_id]['status_work']

    logger.info(f'Registered user: {first_name} {last_name}, phone: {phone}, role: {rool_name}, work status: {status_work}')

    rool, _ = Rool.get_or_create(name=rool_name)

    user = User.create(
        chat_id=chat_id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        rool=rool,
        status_work=status_work
    )
    user.save()

    bot.send_message(chat_id, '✅ ثبت نام شما با موفقیت انجام شد!')

    del user_data[chat_id]

@bot.message_handler(commands=['show_users'])
def show_users(message):
    chat_id = message.chat.id
    logger.info(f'User with chat_id {chat_id} requested to show users')

    user = User.get_or_none(User.chat_id == chat_id)

    if user is None:
        bot.send_message(chat_id, "❌ کاربری با این ID یافت نشد، لطفا ثبت‌نام کنید.")
        return  

    if user.rool.name == 'مستر':
        users = User.select()
        for u in users:
            bot.send_message(
                chat_id, 
                f'👤 نام: {u.first_name}\n'
                f'📛 نام خانوادگی: {u.last_name}\n'
                f'📞 شماره تماس: {u.phone}\n'
                f'🔰 نقش: {u.rool.name}\n'
                f'💼 وضعیت کاری: {u.status_work}'
            )
    else:
        bot.send_message(chat_id, "❌ شما مجاز به مشاهده‌ی کاربران نیستید.")
@bot.message_handler(commands=["send_report"])
def send_reprt_start(message):
    text_report = message.text  
    bot.send_message(message.chat.id, "لطفا متن گزارش خود را بفرستید")  
    bot.register_next_step_handler(message, send_report_finall, text_report)

def send_report_finall(message, text_report):
    user = User.get(chat_id=message.chat.id)  
    report = Report.create(
        user=user,
        date=datetime.now(),
        text=message.text  
    )
    report.save()
    bot.send_message(message.chat.id, "دریافت شد")


@bot.message_handler(commands=["show_reports"])
def show_reports(message):
    try:
        user = User.get(User.chat_id == message.chat.id)  
        reports = Report.select().where(Report.user == user)   
        
        if reports:
            response = "\n\n".join([f"📅 تاریخ: {r.date}\n📝 متن گزارش: {r.text}" for r in reports])
        else:
            response = "⛔ شما هیچ گزارشی ثبت نکرده‌اید."
        
        bot.send_message(message.chat.id, response)
    
    except User.DoesNotExist:
        bot.send_message(message.chat.id, "⛔ شما هنوز در سیستم ثبت نشده‌اید!")


@bot.message_handler(commands=["show_reports_for_master"])
def show_reports_for_master(message):
    try:
        user = User.get(User.chat_id == message.chat.id)  
        if user.rool.name == "مستر":  
            reports = Report.select()
            
            if reports:
                response = "\n\n".join([
                    f"👤 کاربر: {report.user.first_name} {report.user.last_name}\n📅 تاریخ: {report.date}\n📝 گزارش: {report.text}"
                    for report in reports
                ])
            else:
                response = "⛔ هیچ گزارشی ثبت نشده است."
            
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "⛔ شما دسترسی مشاهده گزارش‌ها را ندارید.")

    except User.DoesNotExist:
        bot.send_message(message.chat.id, "⛔ شما هنوز در سیستم ثبت نشده‌اید!")




bot.polling()