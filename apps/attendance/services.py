from django.db import transaction
from rest_framework import serializers

from apps.events.models import Event
from apps.events.tasks import send_event_notification

from .models import Attendance, WaitingList


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
        return "Joined successfully"

    WaitingList.objects.create(user=user, event=event)
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
    send_event_notification.delay(next_waiting.user_id, f"You were moved from waiting list to joined for {event.title}.")
    return attendance
