from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Report


User = get_user_model()


class ReportCreateSerializer(serializers.ModelSerializer):
    target_user_id = serializers.PrimaryKeyRelatedField(source="target_user", queryset=User.objects.all())

    class Meta:
        model = Report
        fields = ("target_user_id", "message")

    def validate(self, attrs):
        if attrs["target_user"] == self.context["request"].user:
            raise serializers.ValidationError("You cannot report yourself.")
        return attrs

    def create(self, validated_data):
        return Report.objects.create(reporter=self.context["request"].user, **validated_data)


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.SerializerMethodField()
    target_user = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ("id", "reporter", "target_user", "message", "created_at")

    @extend_schema_field(serializers.DictField())
    def get_reporter(self, obj):
        return {"id": obj.reporter_id, "full_name": obj.reporter.full_name}

    @extend_schema_field(serializers.DictField())
    def get_target_user(self, obj):
        return {"id": obj.target_user_id, "full_name": obj.target_user.full_name}
