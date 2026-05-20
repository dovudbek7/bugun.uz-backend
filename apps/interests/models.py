from django.conf import settings
from django.db import models


class Interest(models.Model):
    title = models.CharField(max_length=120, unique=True)
    icon = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class UserInterest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_interests")
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, related_name="user_interests")

    class Meta:
        unique_together = ("user", "interest")
        indexes = [models.Index(fields=["user", "interest"])]

    def __str__(self):
        return f"{self.user_id}:{self.interest_id}"
