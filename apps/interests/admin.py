from django.contrib import admin

from apps.common.ai_translate import translate_text

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
        done = failed = 0
        for obj in queryset:
            try:
                result = translate_text(obj.title)
            except Exception:  # noqa: BLE001
                failed += 1
                continue
            if result:
                obj.title_ru = result.get("ru", "")
                obj.title_en = result.get("en", "")
                obj.save(update_fields=["title_ru", "title_en"])
                done += 1
        self.message_user(request, f"Translated {done}, failed {failed}.")


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "interest")
    list_filter = ("interest",)
