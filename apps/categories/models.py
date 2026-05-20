from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=120, unique=True)
    icon = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
