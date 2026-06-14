from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.common.lang import get_request_language

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "title_ru", "title_en", "icon", "color")

    @extend_schema_field(serializers.CharField())
    def get_name(self, obj):
        return obj.get_title(get_request_language(self.context.get("request")))


class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title", "title_ru", "title_en", "icon", "color")
