from telebot import TeleBot
from telebot import logger
from dotenv import load_dotenv
import os
import logging
import datetime
from models import User, Rool, Report, ChatUser
from tasls import app
load_dotenv()

logger.setLevel(logging.INFO)
API_KEY = os.getenv('API_KEY')

bot = TeleBot(API_KEY)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    ChatUser.get_or_create(chat_id=chat_id)
    bot.send_message(message.chat.id, 'خوش آمدید لطفا /register را بزنید')
    bot.send_message(message.chat.id, 'برای مشاهده دستورات /help را بزنید')


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

    # ارسال پیام موفقیت
    bot.send_message(chat_id, '✅ ثبت نام شما با موفقیت انجام شد!')

    # پاک کردن اطلاعات موقت از دیکشنری
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


@bot.message_handler(commands=['delete_user'])
def delete_user(message):
    is_master = User.select().join(Rool).where(Rool.name == 'مستر', User.chat_id == message.chat.id).exists()
    if is_master:
        bot.send_message(message.chat.id, 'لطفا شماره تماس کاربر مورد نظر را وارد کنید:')
        bot.register_next_step_handler(message, end_delete_user)
    else:
        bot.send_message(message.chat.id, '❌ شما مجاز به حذف کاربران نیستید.')

def end_delete_user(message):
    chat_id = message.chat.id
    phone = message.text

    user = User.get_or_none(User.phone == phone)

    if user is None:
        bot.send_message(chat_id, "❌ کاربری با این شماره تماس یافت نشد.")
        return

    user.delete_instance()
    bot.send_message(chat_id, '✅ کاربر با موفقیت حذف شد.')


@bot.message_handler(commands=['send_report'])
def send_report(message):
    chat_id = message.chat.id
    is_master = User.select().join(Rool).where(Rool.name == 'مستر', User.chat_id == chat_id).exists()
    if is_master:
        bot.send_message(chat_id, 'شما نیاز به ارسال گزارش ندارید.')
        return 
    else:
        bot.send_message(chat_id, 'لطفا متن گزارش خود را وارد کنید:')
        bot.register_next_step_handler(message, save_report)

def save_report(message):
    chat_id = message.chat.id
    text = message.text

    user = User.get_or_none(User.chat_id == chat_id)

    if user is None:
        bot.send_message(chat_id, "❌ کاربری با این ID یافت نشد، لطفا ثبت‌نام کنید.")
        return

    report = Report.create(
        user=user,
        date = datetime.datetime.now(),
        text=text
    )
    report.save()

    bot.send_message(chat_id, '✅ گزارش شما با موفقیت ثبت شد!')

@bot.message_handler(commands=['show_reports'])
def show_reports(message):
    chat_id = message.chat.id
    is_user_report = User.select().join(Report).where(User.chat_id == chat_id).exists()

    if is_user_report:
        reports = Report.select()
        for r in reports:
            bot.send_message(
                chat_id, 
                f'👤 نام: {r.user.first_name} {r.user.last_name}\n'
                f'📅 تاریخ: {r.date}\n'
                f'📄 متن گزارش: {r.text}'
            )
    else:
        bot.send_message(chat_id, "❌ شما مجاز به مشاهده‌ی گزارش‌ها نیستید.")


@bot.message_handler(commands=['edit_report'])
def edit_report(message):
    bot.send_message(message.chat.id, 'لطفا تاریخ گزارش مورد نظر را وارد کنید:')
    bot.register_next_step_handler(message, set_edit_report)

def set_edit_report(message):
    chat_id = message.chat.id
    date = message.text

    report = Report.get_or_none(Report.date == date)

    if report is None:
        bot.send_message(chat_id, "❌ گزارشی با این تاریخ یافت نشد.")
        return

    bot.send_message(chat_id, 'لطفا متن جدید گزارش را وارد کنید:')
    user_data[chat_id] = {}
    user_data[chat_id]['date'] = date
    bot.register_next_step_handler(message, set_new_report)

def set_new_report(message):
    chat_id = message.chat.id
    text = message.text

    date = user_data[chat_id]['date']

    report = Report.get(Report.date == date)
    report.text = text
    report.save()

    bot.send_message(chat_id, '✅ گزارش با موفقیت ویرایش شد.')
    del user_data[chat_id]

@bot.message_handler(commands=['delete_report'])
def delete_report(message):
    bot.send_message(message.chat.id, 'لطفا تاریخ گزارش مورد نظر را وارد کنید:')
    bot.register_next_step_handler(message, set_delete_report)    

def set_delete_report(message):
    chat_id = message.chat.id
    date = message.text

    report = Report.get_or_none(Report.date == date)

    if report is None:
        bot.send_message(chat_id, "❌ گزارشی با این تاریخ یافت نشد.")
        return

    report.delete_instance()
    bot.send_message(chat_id, '✅ گزارش با موفقیت حذف شد.')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'راهنمای دستورات:\n'
                                     '/start - شروع\n'
                                     '/register - ثبت‌نام\n'
                                     '/show_users -  فقط مستر اجازه دارد نمایش کاربران\n'
                                     '/send_report - ارسال گزارش\n'
                                     '/show_reports - نمایش گزارش‌ها\n'
                                     '/edit_report - ویرایش گزارش\n'
                                     '/delete_report - حذف گزارش\n'
                                        '/delete_user - حذف کاربر فقط مستر اجازه دارد\n'
                                     '/help - راهنما')
@bot.message_handler(commands=['alert'])
def send_alert(message):
    chat_id = message.chat.id
    send_alert_task.delay(chat_id)  # اجرای تسک به‌صورت غیربلاک‌کننده در Celery
    bot.send_message(chat_id, '✅ پیام هشدار به صف پردازش Celery اضافه شد.')

bot.polling()
