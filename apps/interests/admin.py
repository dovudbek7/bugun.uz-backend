from django.contrib import admin

from apps.common.tasks import translate_taxonomy_obj

from .models import Interest, UserInterest


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "title_ru", "title_en", "icon")
    search_fields = ("title", "title_ru", "title_en")
    readonly_fields = ("title_uz_cyrl",)
    actions = ("retranslate_selected",)

    @admin.display(description="Title (uz_cyrl, auto)")
    def title_uz_cyrl(self, obj):
        return obj.get_title("uz_cyrl")

    @admin.action(description="Re-translate selected (AI, ru/en)")
    def retranslate_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            translate_taxonomy_obj.delay("interests", "Interest", obj.pk)
            count += 1
        self.message_user(request, f"Queued {count} interest(s) for re-translation.")


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "interest")
    list_filter = ("interest",)
