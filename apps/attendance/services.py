import threading
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.events.models import Event
from apps.events.tasks import send_attendance_notification

from .models import Attendance, EventReminder, WaitingList


def _notify(user_id, event_id, notification_type):
    """Run attendance notification in background thread (no Celery needed)."""
    def _run():
        try:
            send_attendance_notification(user_id, event_id, notification_type)
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()


def _maybe_schedule_reminder(user_id, event_pk):
    """Auto-create a 30-min reminder for users who join within 24h of the event."""
    from django.contrib.auth import get_user_model
    event = Event.objects.filter(pk=event_pk).first()
    if not event:
        return
    now = timezone.now()
    time_left = event.starts_at - now
    if timedelta(minutes=30) < time_left <= timedelta(hours=24):
        remind_at = event.starts_at - timedelta(minutes=30)
        user = get_user_model().objects.filter(pk=user_id).first()
        if user:
            EventReminder.objects.update_or_create(
                user=user,
                event=event,
                defaults={"remind_at": remind_at, "sent": False},
            )


def _check_milestone(event_pk):
    from apps.events.tasks import notify_organizer_milestone
    count = Attendance.objects.filter(
        event_id=event_pk, status__in=[Attendance.STATUS_JOINED, Attendance.STATUS_ATTENDED]
    ).count()
    if count > 0 and count % 5 == 0:
        notify_organizer_milestone.delay(event_pk, count)


def ensure_joinable(event):
    if event.status in {Event.STATUS_CANCELLED, Event.STATUS_COMPLETED}:
        raise serializers.ValidationError("Cannot join cancelled or completed events.")
    if event.is_draft:
        raise serializers.ValidationError("Cannot join draft events.")


@transaction.atomic
def join_event(user, event):
    event = Event.objects.select_for_update().get(pk=event.pk)
    ensure_joinable(event)

    existing = Attendance.objects.filter(user=user, event=event).first()
    if existing and existing.status != Attendance.STATUS_CANCELLED:
        raise serializers.ValidationError("You already joined this event.")
    if WaitingList.objects.filter(user=user, event=event).exists():
        raise serializers.ValidationError("You are already in the waiting list.")

    if event.seats_left > 0:
        if existing:
            existing.status = Attendance.STATUS_JOINED
            existing.save(update_fields=["status"])
        else:
            Attendance.objects.create(user=user, event=event, status=Attendance.STATUS_JOINED)
        uid, eid = user.id, event.pk
        transaction.on_commit(lambda: _notify(uid, eid, "joined"))
        transaction.on_commit(lambda: _check_milestone(eid))
        transaction.on_commit(lambda: _maybe_schedule_reminder(uid, eid))
        return "Joined successfully"

    WaitingList.objects.create(user=user, event=event)
    uid, eid = user.id, event.pk
    transaction.on_commit(lambda: _notify(uid, eid, "waiting"))
    return "Added to waiting list"


@transaction.atomic
def leave_event(user, event):
    event = Event.objects.select_for_update().get(pk=event.pk)

    waiting_deleted, _ = WaitingList.objects.filter(user=user, event=event).delete()
    if waiting_deleted:
        return "Left waiting list successfully"

    attendance = Attendance.objects.filter(user=user, event=event).exclude(status=Attendance.STATUS_CANCELLED).first()
    if not attendance:
        raise serializers.ValidationError("You have not joined this event.")

    attendance.status = Attendance.STATUS_CANCELLED
    attendance.save(update_fields=["status"])
    uid, eid = user.id, event.pk
    transaction.on_commit(lambda: _notify(uid, eid, "cancelled"))
    promote_next_waiting_user(event)
    transaction.on_commit(lambda: notify_waiting_positions(event.pk))
    return "Left successfully"


def promote_next_waiting_user(event):
    next_waiting = WaitingList.objects.select_related("user").filter(event=event).first()
    if not next_waiting or event.seats_left <= 0:
        return None

    attendance, _ = Attendance.objects.get_or_create(user=next_waiting.user, event=event)
    attendance.status = Attendance.STATUS_JOINED
    attendance.save(update_fields=["status"])
    next_waiting.delete()
    _notify(next_waiting.user_id, event.pk, "promoted")
    return attendance


def notify_waiting_positions(event_pk):
    from apps.events.tasks import send_position_notification
    waiting = list(WaitingList.objects.filter(event_id=event_pk).order_by("created_at").values_list("user_id", flat=True))
    for idx, user_id in enumerate(waiting):
        pos = idx + 1
        if pos < 5 or pos % 5 == 0:
            send_position_notification.delay(user_id, event_pk, pos)


def promote_all_waiting_users(event):
    """Promote waiting users until no seats left or waiting list empty."""
    from apps.events.models import Event as _Event
    event = _Event.objects.get(pk=event.pk)
    while event.seats_left > 0:
        next_waiting = WaitingList.objects.select_related("user").filter(event=event).first()
        if not next_waiting:
            break
        attendance, _ = Attendance.objects.get_or_create(user=next_waiting.user, event=event)
        attendance.status = Attendance.STATUS_JOINED
        attendance.save(update_fields=["status"])
        next_waiting.delete()
        _notify(next_waiting.user_id, event.pk, "promoted")
        event = _Event.objects.get(pk=event.pk)
