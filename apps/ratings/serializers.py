from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers

from apps.attendance.models import Attendance
from apps.events.models import Event

from .models import Rating


User = get_user_model()


class RatingSerializer(serializers.ModelSerializer):
    event_id = serializers.PrimaryKeyRelatedField(source="event", queryset=Event.objects.all(), write_only=True)

    class Meta:
        model = Rating
        fields = ("to_user", "event_id", "stars")

    def validate(self, attrs):
        request = self.context["request"]
        event = attrs["event"]
        to_user = attrs["to_user"]
        if request.user == to_user:
            raise serializers.ValidationError("You cannot rate yourself.")
        if event.status != Event.STATUS_COMPLETED:
            raise serializers.ValidationError("Event must be completed before rating.")
        attended = Attendance.objects.filter(
            event=event,
            user__in=[request.user, to_user],
            status=Attendance.STATUS_ATTENDED,
        ).count()
        if attended != 2:
            raise serializers.ValidationError("Only attended participants can rate each other.")
        if Rating.objects.filter(from_user=request.user, to_user=to_user, event=event).exists():
            raise serializers.ValidationError("You already rated this user for this event.")
        return attrs

    def create(self, validated_data):
        rating = Rating.objects.create(from_user=self.context["request"].user, **validated_data)
        aggregate = Rating.objects.filter(to_user=rating.to_user).aggregate(avg=Avg("stars"))
        rating.to_user.rating = aggregate["avg"] or 0
        rating.to_user.save(update_fields=["rating", "updated_at"])
        return rating


class LeaderboardSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(source="total_attended")

    class Meta:
        model = User
        fields = ("id", "full_name", "avatar", "score")
