from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import OrganizerApplication


class OrganizerApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizerApplication
        fields = ("message",)

    def validate(self, attrs):
        user = self.context["request"].user
        if user.is_organizer:
            raise serializers.ValidationError("You are already an organizer.")
        if OrganizerApplication.objects.filter(user=user, status=OrganizerApplication.STATUS_PENDING).exists():
            raise serializers.ValidationError("You already have a pending request.")
        return attrs

    def create(self, validated_data):
        return OrganizerApplication.objects.create(user=self.context["request"].user, **validated_data)


class OrganizerApplicationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = OrganizerApplication
        fields = ("id", "user", "message", "status", "created_at")

    @extend_schema_field(serializers.DictField())
    def get_user(self, obj):
        return {"id": obj.user_id, "full_name": obj.user.full_name, "telegram_username": obj.user.telegram_username}
