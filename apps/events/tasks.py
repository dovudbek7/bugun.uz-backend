from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from apps.attendance.models import Attendance
from apps.common.telegram import send_telegram_message, send_telegram_venue

from .models import Event


@shared_task
def send_event_notification(user_id, text):
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.filter(id=user_id).first()
    if user:
        send_telegram_message(user.telegram_id, text)


@shared_task
def send_attendance_notification(user_id, event_id, notification_type):
    """
    notification_type: joined | waiting | cancelled | promoted
    Sends translated text + venue (for joined/promoted).
    """
    import html as html_module
    from django.conf import settings as django_settings
    from django.contrib.auth import get_user_model
    from apps.telegram_bot.translations import t

    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    if not user or not user.telegram_id:
        return

    event = Event.objects.select_related("location").filter(id=event_id).first()
    if not event:
        return

    lang = user.language or "uz_latn"
    loc = event.location
    kwargs = {
        "title": html_module.escape(event.title),
        "date": event.event_date.strftime("%d.%m.%Y"),
        "time": event.event_time.strftime("%H:%M"),
        "location": html_module.escape(loc.title),
        "address": html_module.escape(loc.address),
    }
    text = t(f"event_{notification_type}", lang).format(**kwargs)

    reply_markup = None
    mini_app_url = getattr(django_settings, "MINI_APP_URL", "").rstrip("/")
    if mini_app_url and notification_type not in ("cancelled", "waiting"):
        if notification_type == "joined":
            reply_markup = {
                "inline_keyboard": [[
                    {"text": t("open_event", lang), "web_app": {"url": f"{mini_app_url}/activity/{event_id}"}},
                    {"text": t("remind_me", lang), "callback_data": f"remind:{event_id}"},
                ]]
            }
        else:
            reply_markup = {
                "inline_keyboard": [[
                    {"text": t("open_event", lang), "web_app": {"url": f"{mini_app_url}/activity/{event_id}"}}
                ]]
            }

    send_telegram_message(user.telegram_id, text, reply_markup=reply_markup)

    if notification_type in ("joined", "promoted"):
        send_telegram_venue(
            user.telegram_id,
            float(loc.latitude),
            float(loc.longitude),
            loc.title,
            loc.address,
        )


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
                send_attendance_notification.delay(attendance.user_id, event.pk, "reminder")
                sent += 1
            event.reminder_sent = True
            event.save(update_fields=["reminder_sent", "updated_at"])
    return sent


@shared_task
def send_scheduled_reminders():
    from apps.attendance.models import EventReminder
    now = timezone.localtime()
    reminders = (
        EventReminder.objects
        .filter(remind_at__lte=now, sent=False)
        .select_related("user", "event")
    )
    sent = 0
    for reminder in reminders:
        send_attendance_notification.delay(reminder.user_id, reminder.event_id, "reminder")
        reminder.sent = True
        reminder.save(update_fields=["sent"])
        sent += 1
    return sent
