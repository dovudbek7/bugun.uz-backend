from django.contrib import admin

from .models import OrganizerApplication


@admin.register(OrganizerApplication)
class OrganizerApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__full_name", "message")
    actions = ("approve_requests", "reject_requests")

    @admin.action(description="Approve selected organizer requests")
    def approve_requests(self, request, queryset):
        for application in queryset.select_related("user"):
            application.status = OrganizerApplication.STATUS_APPROVED
            application.save(update_fields=["status"])
            application.user.is_organizer = True
            application.user.save(update_fields=["is_organizer"])

    @admin.action(description="Reject selected organizer requests")
    def reject_requests(self, request, queryset):
        queryset.update(status=OrganizerApplication.STATUS_REJECTED)
