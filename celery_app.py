from celery import Celery
import os

app = Celery(
    'tasks',
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND")
)
app.conf.beat_schedule = {
    'send-alert-every-30-seconds': {
        'task': 'config.bot_commands.send_alert_task',
        'schedule': 30.0,
    },
}
