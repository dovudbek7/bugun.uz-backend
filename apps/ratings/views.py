from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import mixins, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.attendance.models import Attendance

from .models import Rating
from .serializers import LeaderboardSerializer, RatingSerializer


User = get_user_model()


class RatingViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Rating submitted"}, status=status.HTTP_201_CREATED)


class LeaderboardView(ListAPIView):
    serializer_class = LeaderboardSerializer
    pagination_class = None

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        att_filter = Q(
            attendances__status__in=[Attendance.STATUS_JOINED, Attendance.STATUS_ATTENDED]
        )
        if start_date:
            att_filter &= Q(attendances__event__event_date__gte=start_date)
        if end_date:
            att_filter &= Q(attendances__event__event_date__lte=end_date)

        return (
            User.objects
            .annotate(score=Count("attendances", filter=att_filter))
            .filter(score__gt=0)
            .order_by("-score", "-rating")[:100]
        )
