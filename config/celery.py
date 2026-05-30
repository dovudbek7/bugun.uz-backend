import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("community_platform")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send-event-reminders": {
        "task": "apps.events.tasks.send_event_reminders",
        "schedule": crontab(minute="*/30"),
    },
    "send-scheduled-reminders": {
        "task": "apps.events.tasks.send_scheduled_reminders",
        "schedule": crontab(minute="*/5"),
    },
    "complete-past-events": {
        "task": "apps.events.tasks.complete_past_events",
        "schedule": crontab(minute="*/15"),
    },
}
