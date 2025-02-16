from telebot import TeleBot
from telebot import logger
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import time
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

@bot.message_handler(commands=['show_user_profile'])
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

@bot.message_handler(commands=["show_users"])
def show_users(message):
    try:
        user = User.get(User.chat_id == message.chat.id)   

        if user.rool.name == "مستر":  
            users = User.select()
            
            if users:
                response = "\n\n".join([
                    f"👤 نام: {u.first_name} {u.last_name}\n📞 تلفن: {u.phone}\n🔄 وضعیت کاری: {u.status_work}"
                    for u in users
                ])
            else:
                response = "⛔ هیچ کاربری در سیستم ثبت نشده است."
            
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "⛔ شما دسترسی مشاهده کاربران را ندارید.")

    except User.DoesNotExist:
        bot.send_message(message.chat.id, "⛔ شما هنوز در سیستم ثبت نشده‌اید!")



@bot.message_handler(commands=["edit_user_phone"])
def start_edit_user(message):
    bot.send_message(message.chat.id, "📞 لطفا تلفن جدید خود را وارد کنید:")
    bot.register_next_step_handler(message, set_update_user)

def set_update_user(message):
    phone_set = message.text  
    
    user = User.get_or_none(User.chat_id == message.chat.id)  
    
    if user:
        user.phone = phone_set  
        user.save()  
        bot.send_message(message.chat.id, "✅ شماره تلفن شما با موفقیت به‌روزرسانی شد.")
    else:
        bot.send_message(message.chat.id, "⛔ شما هنوز در سیستم ثبت نشده‌اید!")


@bot.message_handler(commands=["edit_first_name"])
def start_edit_first_name(message):
    bot.send_message(message.chat.id, "✏ لطفا نام جدید خود را وارد کنید:")
    bot.register_next_step_handler(message, set_update_first_name)

def set_update_first_name(message):
    user = User.get_or_none(User.chat_id == message.chat.id)
    
    if user:
        user.first_name = message.text   
        user.save()
        bot.send_message(message.chat.id, "✅ نام شما با موفقیت به‌روزرسانی شد.")
    else:
        bot.send_message(message.chat.id, "⛔ شما هنوز در سیستم ثبت نشده‌اید!")


@bot.message_handler(commands=["edit_last_name"])
def start_edit_last_name(message):
    bot.send_message(message.chat.id, "✏ لطفا نام خانوادگی جدید خود را وارد کنید:")
    bot.register_next_step_handler(message, set_update_last_name)

def set_update_last_name(message):
    user = User.get_or_none(User.chat_id == message.chat.id)
    
    if user:
        user.last_name = message.text  
        user.save()
        bot.send_message(message.chat.id, "✅ نام خانوادگی شما با موفقیت به‌روزرسانی شد.")
    else:
        bot.send_message(message.chat.id, "⛔ شما هنوز در سیستم ثبت نشده‌اید!")


@bot.message_handler(commands=["edit_status_work"])
def start_edit_status_work(message):
    bot.send_message(message.chat.id, "🔄 لطفا وضعیت کاری جدید خود را وارد کنید:")
    bot.register_next_step_handler(message, set_update_status_work)

def set_update_status_work(message):
    user = User.get_or_none(User.chat_id == message.chat.id)
    
    if user:
        user.status_work = message.text 
        user.save()
        bot.send_message(message.chat.id, "✅ وضعیت کاری شما با موفقیت به‌روزرسانی شد.")
    else:
        bot.send_message(message.chat.id, "⛔ شما هنوز در سیستم ثبت نشده‌اید!")






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

@bot.message_handler(commands=["help"])
def help_command(message):
    help_text = """
📌 **راهنمای ربات مدیریت کاربران و گزارشات** 📌

✅ **دستورات ثبت‌نام و ویرایش اطلاعات** ✅
➖ `/register` → ثبت‌نام کاربر جدید  
➖ `/edit_user_phone` → ویرایش شماره تلفن  
➖ `/edit_first_name` → ویرایش نام  
➖ `/edit_last_name` → ویرایش نام خانوادگی  
➖ `/edit_status_work` → ویرایش وضعیت کاری  

✅ **دستورات مربوط به کاربران** ✅
➖ `/show_user_profile` → مشاهده اطلاعات خود  
➖ `/show_users` → (فقط برای مستر) نمایش لیست تمام کاربران  

✅ **دستورات ثبت و نمایش گزارشات** ✅
➖ `/send_report` → ارسال گزارش جدید  
➖ `/show_reports` → مشاهده گزارش‌های خود  
➖ `/show_reports_for_master` → (فقط برای مستر) مشاهده تمام گزارش‌ها  

❓ **سوالات بیشتر دارید؟**  
با ارسال `/help` دوباره، این راهنما را مشاهده کنید. 😊
"""
    bot.send_message(message.chat.id, help_text)


def send_nightly_report_reminder():
    users = User.select().where(User.status_work == "بیکار")
    for user in users:
        bot.send_message(user.chat_id, "🔔 لطفاً گزارش روزانه خود را ارسال کنید: /send_report")

scheduler = BackgroundScheduler()
scheduler.add_job(send_nightly_report_reminder, 'cron', hour=21, minute=0) 
scheduler.start()



bot.polling()