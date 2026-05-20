from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "target_user", "created_at")
    search_fields = ("reporter__full_name", "target_user__full_name", "message")
    list_filter = ("created_at",)
