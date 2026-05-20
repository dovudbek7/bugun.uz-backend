import hashlib
import hmac
import urllib.parse

from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.achievements.serializers import AchievementSerializer
from apps.attendance.models import Attendance
from apps.interests.models import Interest, UserInterest
from apps.interests.serializers import InterestSerializer


User = get_user_model()


class TelegramLoginSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    telegram_username = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.URLField(required=False, allow_blank=True)
    language = serializers.ChoiceField(choices=User.LANGUAGE_CHOICES, default=User.LANGUAGE_UZ_LATN)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        telegram_id = validated_data["telegram_id"]
        defaults = {
            "username": f"tg_{telegram_id}",
            "telegram_username": validated_data.get("telegram_username", ""),
            "avatar": validated_data.get("avatar", ""),
            "language": validated_data.get("language", User.LANGUAGE_UZ_LATN),
            "phone_number": validated_data.get("phone_number", ""),
        }
        user, created = User.objects.get_or_create(telegram_id=telegram_id, defaults=defaults)
        if not created:
            update_fields = []
            for field in ("telegram_username", "avatar", "language", "phone_number"):
                if field in validated_data and validated_data[field]:
                    setattr(user, field, validated_data[field])
                    update_fields.append(field)
            if update_fields:
                user.save(update_fields=[*update_fields, "updated_at"])
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "is_organizer": user.is_organizer,
            },
        }


class TelegramWebAppLoginSerializer(serializers.Serializer):
    init_data = serializers.CharField()

    def validate_init_data(self, value):
        parsed = dict(urllib.parse.parse_qsl(value, strict_parsing=True))
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            raise serializers.ValidationError("hash missing")

        data_check = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected_hash = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_hash, received_hash):
            raise serializers.ValidationError("invalid hash")

        return parsed

    def create(self, validated_data):
        parsed = validated_data["init_data"]
        import json
        tg_user = json.loads(parsed.get("user", "{}"))
        tg_id = tg_user.get("id")
        if not tg_id:
            raise serializers.ValidationError("user id missing")

        username = tg_user.get("username", "")
        full_name = " ".join(filter(None, [tg_user.get("first_name", ""), tg_user.get("last_name", "")])) or username

        user, created = User.objects.get_or_create(
            telegram_id=tg_id,
            defaults={
                "username": f"tg_{tg_id}",
                "telegram_username": username,
                "full_name": full_name,
            },
        )
        if not created and username and user.telegram_username != username:
            user.telegram_username = username
            user.save(update_fields=["telegram_username", "updated_at"])

        refresh = RefreshToken.for_user(user)
        needs_onboarding = not bool(user.phone_number)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "needs_onboarding": needs_onboarding,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "is_organizer": user.is_organizer,
            },
        }


class OnboardingSerializer(serializers.ModelSerializer):
    interests = serializers.PrimaryKeyRelatedField(queryset=Interest.objects.all(), many=True, required=False)

    class Meta:
        model = User
        fields = ("full_name", "age", "region", "phone_number", "show_telegram", "interests")

    def update(self, instance, validated_data):
        interests = validated_data.pop("interests", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if interests is not None:
            UserInterest.objects.filter(user=instance).delete()
            UserInterest.objects.bulk_create([UserInterest(user=instance, interest=interest) for interest in interests])
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    interests = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "telegram_username",
            "avatar",
            "age",
            "region",
            "phone_number",
            "language",
            "show_telegram",
            "is_organizer",
            "total_attended",
            "rating",
            "interests",
            "achievements",
            "history",
        )
        read_only_fields = ("is_organizer", "total_attended", "rating")

    @extend_schema_field(InterestSerializer(many=True))
    def get_interests(self, obj):
        interests = Interest.objects.filter(user_interests__user=obj)
        return InterestSerializer(interests, many=True).data

    @extend_schema_field(AchievementSerializer(many=True))
    def get_achievements(self, obj):
        achievements = [ua.achievement for ua in obj.user_achievements.select_related("achievement").all()]
        return AchievementSerializer(achievements, many=True).data

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_history(self, obj):
        attendances = (
            Attendance.objects.filter(user=obj)
            .select_related("event")
            .order_by("-event__event_date", "-event__event_time")[:20]
        )
        return [
            {"event": {"id": item.event_id, "title": item.event.title}, "status": item.status, "date": item.event.event_date}
            for item in attendances
        ]


class ProfileUpdateSerializer(OnboardingSerializer):
    class Meta(OnboardingSerializer.Meta):
        fields = ("full_name", "age", "region", "phone_number", "show_telegram", "language", "interests")


class HistorySerializer(serializers.ModelSerializer):
    event = serializers.SerializerMethodField()
    date = serializers.DateField(source="event.event_date")

    class Meta:
        model = Attendance
        fields = ("event", "status", "date")

    @extend_schema_field(serializers.DictField())
    def get_event(self, obj):
        return {"id": obj.event_id, "title": obj.event.title}
