from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "full_name", "telegram_id", "telegram_username", "is_organizer", "total_attended", "rating")
    list_filter = ("is_organizer", "language", "is_staff")
    search_fields = ("full_name", "telegram_username", "telegram_id", "phone_number")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Telegram profile",
            {
                "fields": (
                    "telegram_id",
                    "telegram_username",
                    "full_name",
                    "avatar",
                    "age",
                    "region",
                    "phone_number",
                    "language",
                    "show_telegram",
                    "is_organizer",
                    "total_attended",
                    "rating",
                )
            },
        ),
    )
