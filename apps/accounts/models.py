import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


def _referral_code():
    return uuid.uuid4().hex[:10]


class User(AbstractUser):
    LANGUAGE_UZ_LATN = "uz_latn"
    LANGUAGE_UZ_CYRL = "uz_cyrl"
    LANGUAGE_RU = "ru"
    LANGUAGE_EN = "en"
    LANGUAGE_CHOICES = (
        (LANGUAGE_UZ_LATN, "Uzbek Latin"),
        (LANGUAGE_UZ_CYRL, "Uzbek Cyrillic"),
        (LANGUAGE_RU, "Russian"),
        (LANGUAGE_EN, "English"),
    )

    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, db_index=True)
    telegram_username = models.CharField(max_length=255, blank=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.URLField(blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    region = models.CharField(max_length=120, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    language = models.CharField(max_length=12, choices=LANGUAGE_CHOICES, default=LANGUAGE_UZ_LATN)
    show_telegram = models.BooleanField(default=True)
    is_organizer = models.BooleanField(default=False)
    total_attended = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    last_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    referral_code = models.CharField(max_length=10, unique=True, default=_referral_code)
    referred_by = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="referrals"
    )
    referral_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["telegram_id"]),
            models.Index(fields=["is_organizer"]),
            models.Index(fields=["total_attended", "rating"]),
        ]

    def __str__(self):
        return self.full_name or self.telegram_username or self.username


class UserFollow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        indexes = [models.Index(fields=["following", "created_at"])]

    def __str__(self):
        return f"{self.follower_id}->{self.following_id}"
