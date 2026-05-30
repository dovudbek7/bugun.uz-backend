from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.attendance.models import Attendance, WaitingList
from apps.categories.serializers import CategorySerializer
from apps.locations.serializers import LocationSerializer

from .models import Event


class EventOrganizerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()


class ParticipantPreviewSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(source="user.avatar")

    class Meta:
        model = Attendance
        fields = ("id", "avatar")


class EventListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    location = LocationSerializer()
    seats_left = serializers.IntegerField(read_only=True)
    waiting_count = serializers.IntegerField(read_only=True)
    participants = serializers.SerializerMethodField()
    organizer = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "image",
            "category",
            "location",
            "event_date",
            "event_time",
            "total_seats",
            "seats_left",
            "waiting_count",
            "status",
            "participants",
            "organizer",
        )

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_participants(self, obj):
        items = obj.attendances.filter(status__in=[Attendance.STATUS_JOINED, Attendance.STATUS_ATTENDED]).select_related("user")[:10]
        return [{"id": item.user_id, "avatar": item.user.avatar} for item in items]

    @extend_schema_field(serializers.DictField())
    def get_organizer(self, obj):
        return {"id": obj.organizer_id, "full_name": obj.organizer.full_name, "avatar": obj.organizer.avatar}


class EventDetailSerializer(EventListSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta(EventListSerializer.Meta):
        fields = EventListSerializer.Meta.fields + ("created_at",)


class EventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("category", "location", "title", "description", "image", "event_date", "event_time", "total_seats", "is_draft")

    def validate_total_seats(self, value):
        if value <= 0:
            raise serializers.ValidationError("total_seats must be greater than zero.")
        return value

    def create(self, validated_data):
        return Event.objects.create(organizer=self.context["request"].user, **validated_data)


class EventSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "title")


class ParticipantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    full_name = serializers.CharField(source="user.full_name")
    avatar = serializers.CharField(source="user.avatar")

    class Meta:
        model = Attendance
        fields = ("id", "full_name", "avatar", "status")


class WaitingListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = WaitingList
        fields = ("id", "user")

    @extend_schema_field(serializers.DictField())
    def get_user(self, obj):
        return {"id": obj.user_id, "full_name": obj.user.full_name}


class EventMapSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    icon = serializers.CharField(source="category.icon")
    time = serializers.TimeField(source="event_time")
    seats_left = serializers.IntegerField(read_only=True)
    name = serializers.CharField(source="title")

    class Meta:
        model = Event
        fields = ("id", "name", "icon", "time", "seats_left", "location")

    @extend_schema_field(serializers.DictField())
    def get_location(self, obj):
        loc = obj.location
        return {
            "title": loc.title,
            "latitude": str(loc.latitude),
            "longitude": str(loc.longitude),
        }
