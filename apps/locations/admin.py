from django.contrib import admin

from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "address", "latitude", "longitude")
    search_fields = ("title", "address")
