from django.conf import settings
from django.db import models


class Attendance(models.Model):
    STATUS_JOINED = "joined"
    STATUS_ATTENDED = "attended"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (STATUS_JOINED, "Joined"),
        (STATUS_ATTENDED, "Attended"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendances")
    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="attendances")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_JOINED)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")
        ordering = ["-joined_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["event", "status"]),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.event_id}:{self.status}"


class WaitingList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="waiting_entries")
    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="waiting_list")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")
        ordering = ["created_at"]
        indexes = [models.Index(fields=["event", "created_at"])]

    def __str__(self):
        return f"{self.user_id}:{self.event_id}"


class EventReminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="event_reminders")
    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="reminders")
    remind_at = models.DateTimeField()
    sent = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "event")
        indexes = [models.Index(fields=["remind_at", "sent"])]

    def __str__(self):
        return f"{self.user_id}:{self.event_id}@{self.remind_at}"
