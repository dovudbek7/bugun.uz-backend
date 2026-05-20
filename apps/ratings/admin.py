from django.contrib import admin

from .models import Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "from_user", "to_user", "event", "stars", "created_at")
    list_filter = ("stars", "event")
    search_fields = ("from_user__full_name", "to_user__full_name", "event__title")
