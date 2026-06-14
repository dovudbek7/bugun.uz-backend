from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.common.lang import get_request_language

from .models import Interest


class InterestSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Interest
        fields = ("id", "title", "title_ru", "title_en", "icon")

    @extend_schema_field(serializers.CharField())
    def get_title(self, obj):
        return obj.get_title(get_request_language(self.context.get("request")))
