from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from apps.attendance.models import Attendance
from apps.common.telegram import send_telegram_message

from .models import Event


@shared_task
def send_event_notification(user_id, text):
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.filter(id=user_id).first()
    if user:
        send_telegram_message(user.telegram_id, text)


@shared_task
def complete_past_events():
    now = timezone.localtime()
    completed = Event.objects.filter(
        Q(event_date__lt=now.date()) | Q(event_date=now.date(), event_time__lt=now.time()),
        status=Event.STATUS_UPCOMING,
        is_draft=False,
    ).update(status=Event.STATUS_COMPLETED)
    return completed


@shared_task
def send_event_reminders():
    now = timezone.localtime()
    until = now + timedelta(hours=24)
    events = Event.objects.filter(
        status=Event.STATUS_UPCOMING,
        is_draft=False,
        reminder_sent=False,
        event_date__range=(now.date(), until.date()),
    )
    sent = 0
    for event in events:
        if now <= event.starts_at <= until:
            attendances = Attendance.objects.filter(event=event, status=Attendance.STATUS_JOINED).select_related("user")
            for attendance in attendances:
                send_event_notification.delay(attendance.user_id, f"Reminder: {event.title} starts on {event.event_date} at {event.event_time}.")
                sent += 1
            event.reminder_sent = True
            event.save(update_fields=["reminder_sent", "updated_at"])
    return sent
