from celery import Celery

celery_app = Celery(
    'tasks',
    broker='pyamqp://guest@rabbitmq:5672//',
    backend='rpc://'
)

celery_app.conf.beat_schedule = {
    'send-alert-every-30-seconds': {
        'task': 'main.send_alert_task',
        'schedule': 30.0,
    },
}