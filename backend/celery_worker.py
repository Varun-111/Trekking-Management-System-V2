from celery import Celery
from celery.schedules import crontab
from config import Config


def make_celery():
    celery_app = Celery(
        "trekking_jobs",
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=["scheduled_tasks"],
    )
    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="Asia/Kolkata",
        enable_utc=True,
    )
    celery_app.conf.beat_schedule = {
        "daily-trek-reminders": {
            "task": "scheduled_tasks.send_daily_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
        "monthly-admin-report": {
            "task": "scheduled_tasks.generate_monthly_report",
            "schedule": crontab(day_of_month=1, hour=6, minute=0),
        },
    }
    return celery_app


celery = make_celery()
