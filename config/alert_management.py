from telebot import TeleBot
from tasks import send_alert_task

def alert_handlers(bot: TeleBot):
    @bot.message_handler(commands=['alert'])
    def send_alert(message):
        chat_id = message.chat.id
        send_alert_task.delay(chat_id)
        bot.send_message(chat_id, '✅ پیام هشدار به صف پردازش Celery اضافه شد.')
