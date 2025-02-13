from celery.schedules import crontab
from tasks import request_daily_report
from tasks import app
app.conf.beat_schedule = {
    "request-daily-report-every-day": {
        "task": "tasks.request_daily_report",
        "schedule": crontab(hour=9, minute=0), 
    },
}
app.conf.timezone = "Asia/Tehran"  