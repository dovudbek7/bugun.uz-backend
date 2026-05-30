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
        "reason": html_module.escape(event.cancellation_reason or "—"),
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
    events = Event.objects.filter(
        Q(event_date__lt=now.date()) | Q(event_date=now.date(), event_time__lt=now.time()),
        status=Event.STATUS_UPCOMING,
        is_draft=False,
    )
    count = 0
    for event in events:
        event.status = Event.STATUS_COMPLETED
        event.save(update_fields=["status", "updated_at"])
        send_organizer_rating_prompt.delay(event.pk)
        count += 1
    return count


@shared_task
def send_organizer_rating_prompt(event_id):
    import html as html_module
    from django.conf import settings as django_settings
    from apps.ratings.models import Rating
    from apps.telegram_bot.translations import t

    event = Event.objects.select_related("organizer").filter(pk=event_id).first()
    if not event:
        return

    attendances = Attendance.objects.filter(
        event=event, status=Attendance.STATUS_ATTENDED
    ).select_related("user")

    mini_app_url = getattr(django_settings, "MINI_APP_URL", "").rstrip("/")

    for attendance in attendances:
        user = attendance.user
        if not user.telegram_id:
            continue
        if user.id == event.organizer_id:
            continue
        already_rated = Rating.objects.filter(
            from_user=user, to_user=event.organizer, event=event
        ).exists()
        if already_rated:
            continue

        lang = user.language or "uz_latn"
        text = t("rate_organizer_prompt", lang).format(
            title=html_module.escape(event.title),
            organizer=html_module.escape(event.organizer.full_name or event.organizer.telegram_username or ""),
        )
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "⭐", "callback_data": f"rate_org:{event_id}:1"},
                    {"text": "⭐⭐", "callback_data": f"rate_org:{event_id}:2"},
                    {"text": "⭐⭐⭐", "callback_data": f"rate_org:{event_id}:3"},
                    {"text": "⭐⭐⭐⭐", "callback_data": f"rate_org:{event_id}:4"},
                    {"text": "⭐⭐⭐⭐⭐", "callback_data": f"rate_org:{event_id}:5"},
                ],
                [{"text": t("rate_organizer_skip", lang), "callback_data": f"rate_org_skip:{event_id}"}],
            ]
        }
        send_telegram_message(user.telegram_id, text, reply_markup=reply_markup)


@shared_task
def send_position_notification(user_id, event_id, position):
    import html as html_module
    from django.contrib.auth import get_user_model
    from apps.telegram_bot.translations import t

    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    if not user or not user.telegram_id:
        return
    event = Event.objects.filter(id=event_id).first()
    if not event:
        return
    lang = user.language or "uz_latn"
    text = t("waiting_position_update", lang).format(
        title=html_module.escape(event.title),
        position=position,
    )
    send_telegram_message(user.telegram_id, text)


@shared_task
def send_new_event_notification(user_id, event_id):
    import html as html_module
    from django.contrib.auth import get_user_model
    from apps.telegram_bot.translations import t

    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    if not user or not user.telegram_id:
        return
    event = Event.objects.select_related("organizer").filter(id=event_id).first()
    if not event:
        return
    lang = user.language or "uz_latn"
    text = t("new_event_from_organizer", lang).format(
        organizer=html_module.escape(event.organizer.full_name or event.organizer.telegram_username or ""),
        title=html_module.escape(event.title),
        date=event.event_date.strftime("%d.%m.%Y"),
        time=event.event_time.strftime("%H:%M"),
    )
    from django.conf import settings as django_settings
    mini_app_url = getattr(django_settings, "MINI_APP_URL", "").rstrip("/")
    reply_markup = None
    if mini_app_url:
        reply_markup = {
            "inline_keyboard": [[
                {"text": t("open_event", lang), "web_app": {"url": f"{mini_app_url}/activity/{event_id}"}}
            ]]
        }
    send_telegram_message(user.telegram_id, text, reply_markup=reply_markup)


@shared_task
def notify_category_subscribers(event_id):
    from apps.categories.models import CategorySubscription
    event = Event.objects.filter(pk=event_id).first()
    if not event:
        return
    subs = CategorySubscription.objects.filter(
        category=event.category
    ).exclude(user_id=event.organizer_id).values_list("user_id", flat=True)
    for user_id in subs:
        send_new_event_notification.delay(user_id, event_id)


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
