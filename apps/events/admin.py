from django.contrib import admin

from apps.events.tasks import translate_event

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "organizer", "category", "event_date", "event_time", "status", "is_draft", "total_seats", "translation_status")
    list_filter = ("status", "is_draft", "category", "event_date", "translation_status")
    search_fields = ("title", "description", "organizer__full_name", "location__title")
    autocomplete_fields = ("organizer", "category", "location")
    readonly_fields = ("description_uz_cyrl", "translated_at")
    actions = ("retranslate_selected",)

    @admin.display(description="Description (uz_cyrl, auto)")
    def description_uz_cyrl(self, obj):
        return obj.get_description("uz_cyrl")

    @admin.action(description="Re-translate selected events (AI)")
    def retranslate_selected(self, request, queryset):
        count = 0
        for event in queryset:
            event.translation_status = Event.TRANSLATION_PENDING
            event.save(update_fields=["translation_status", "updated_at"])
            translate_event.delay(event.pk)
            count += 1
        self.message_user(request, f"Queued {count} event(s) for re-translation.")
