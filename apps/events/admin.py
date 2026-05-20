from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "organizer", "category", "event_date", "event_time", "status", "is_draft", "total_seats")
    list_filter = ("status", "is_draft", "category", "event_date")
    search_fields = ("title", "description", "organizer__full_name", "location__title")
    autocomplete_fields = ("organizer", "category", "location")
