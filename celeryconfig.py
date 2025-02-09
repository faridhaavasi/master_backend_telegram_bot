from celery.schedules import crontab
from tasls import app
app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'main.send_alert',
        'schedule': 30.0,
    },
}
