from celery import Celery
from telebot import TeleBot
from dotenv import load_dotenv
import os
import asyncio

from models import User  

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیم Celery با Redis
app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

API_KEY = os.getenv('API_KEY')
async_bot = TeleBot(API_KEY)

@app.task
def request_daily_report():
 
    idle_users = User.select().where(User.status_work == "بی‌کار")
    
    async def send_messages():
        for user in idle_users:
            message = f"🔔 سلام {user.first_name}!\nشما هنوز گزارشی برای امروز ارسال نکرده‌اید. لطفاً گزارش روزانه خود را ارسال کنید."
            await async_bot.send_message(user.chat_id, message)

    asyncio.run(send_messages())
    
    return f"Daily report request sent to {len(idle_users)} idle users."
