from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Rating(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings_given")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings_received")
    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="ratings")
    stars = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user", "event")
        indexes = [
            models.Index(fields=["to_user", "stars"]),
            models.Index(fields=["event"]),
        ]

    def __str__(self):
        return f"{self.from_user_id}->{self.to_user_id}:{self.stars}"
