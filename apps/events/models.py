from django.conf import settings
from django.db import models
from django.utils import timezone


class Event(models.Model):
    STATUS_UPCOMING = "upcoming"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (STATUS_UPCOMING, "Upcoming"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organized_events")
    category = models.ForeignKey("categories.Category", on_delete=models.PROTECT, related_name="events")
    location = models.ForeignKey("locations.Location", on_delete=models.PROTECT, related_name="events")
    title = models.CharField(max_length=180)
    description = models.TextField()
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    event_date = models.DateField()
    event_time = models.TimeField()
    total_seats = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    is_draft = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    cancellation_reason = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event_date", "event_time"]
        indexes = [
            models.Index(fields=["status", "is_draft"]),
            models.Index(fields=["event_date", "event_time"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["organizer", "status"]),
            models.Index(fields=["title"]),
        ]

    @property
    def starts_at(self):
        return timezone.make_aware(
            timezone.datetime.combine(self.event_date, self.event_time),
            timezone.get_current_timezone(),
        )

    @property
    def joined_count(self):
        return self.attendances.filter(status__in=["joined", "attended"]).count()

    @property
    def seats_left(self):
        return max(self.total_seats - self.joined_count, 0)

    @property
    def waiting_count(self):
        return self.waiting_list.count()

    def __str__(self):
        return self.title
