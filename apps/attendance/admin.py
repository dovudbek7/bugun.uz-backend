from django.contrib import admin

from .models import Attendance, WaitingList


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "event", "status", "joined_at")
    list_filter = ("status", "event")
    search_fields = ("user__full_name", "event__title")


@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "event", "created_at")
    search_fields = ("user__full_name", "event__title")
