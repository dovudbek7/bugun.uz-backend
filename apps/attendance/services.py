import threading

from django.db import transaction
from rest_framework import serializers

from apps.events.models import Event
from apps.events.tasks import send_attendance_notification

from .models import Attendance, WaitingList


def _notify(user_id, event_id, notification_type):
    """Run attendance notification in background thread (no Celery needed)."""
    def _run():
        try:
            send_attendance_notification(user_id, event_id, notification_type)
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()


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
        return "Joined successfully"

    WaitingList.objects.create(user=user, event=event)
    uid, eid = user.id, event.pk
    transaction.on_commit(lambda: _notify(uid, eid, "waiting"))
    return "Added to waiting list"


@transaction.atomic
def leave_event(user, event):
    event = Event.objects.select_for_update().get(pk=event.pk)
    attendance = Attendance.objects.filter(user=user, event=event).first()
    if attendance:
        attendance.status = Attendance.STATUS_CANCELLED
        attendance.save(update_fields=["status"])
    else:
        deleted, _ = WaitingList.objects.filter(user=user, event=event).delete()
        if not deleted:
            raise serializers.ValidationError("You have not joined this event.")

    uid, eid = user.id, event.pk
    transaction.on_commit(lambda: _notify(uid, eid, "cancelled"))
    promote_next_waiting_user(event)
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
