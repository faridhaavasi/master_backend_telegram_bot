import telebot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API token from .env
API_TOKEN = os.getenv('API_TOKEN')

if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set or is empty!")

bot = telebot.TeleBot(token=API_TOKEN)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")

# Handle all other messages with content_type 'text'
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()
