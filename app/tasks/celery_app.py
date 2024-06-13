from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=[
        "app.tasks.tasks",
        "app.tasks.scheduled",
    ],
)

celery_app.conf.beat_schedule = {
    "notification_of_booking_for_tomorrow": {
        "task": "notification_for_tomorrow",
        # "schedule": crontab(hour="9"),
        "schedule": 5,
    },
    "notification_of_booking_per_3_days": {
        "task": "notification_per_3_days",
        # "schedule": crontab(minute="30", hour="15"),
        "schedule": 5,
    },
}
