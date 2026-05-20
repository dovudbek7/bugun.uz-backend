from django.contrib import admin

from .models import Interest, UserInterest


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "icon")
    search_fields = ("title",)


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "interest")
    list_filter = ("interest",)
