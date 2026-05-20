from django.conf import settings
from django.db import models


class Interest(models.Model):
    title = models.CharField(max_length=120, unique=True)   # uz_latn (default)
    title_ru = models.CharField(max_length=120, blank=True)
    title_en = models.CharField(max_length=120, blank=True)
    icon = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_title(self, lang: str = "uz_latn") -> str:
        from apps.telegram_bot.translations import latin_to_cyrillic
        if lang == "uz_cyrl":
            return latin_to_cyrillic(self.title)
        if lang == "ru" and self.title_ru:
            return self.title_ru
        if lang == "en" and self.title_en:
            return self.title_en
        return self.title


class UserInterest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_interests")
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, related_name="user_interests")

    class Meta:
        unique_together = ("user", "interest")
        indexes = [models.Index(fields=["user", "interest"])]

    def __str__(self):
        return f"{self.user_id}:{self.interest_id}"
