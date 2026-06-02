from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.attendance.models import Attendance

from .models import Rating
from .serializers import LeaderboardSerializer, RatingSerializer


User = get_user_model()


@extend_schema(tags=["Ratings"])
class RatingViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    @extend_schema(
        summary="Submit rating for an event",
        responses={201: inline_serializer("RatingCreated", fields={"message": serializers.CharField()})},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Rating submitted"}, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Ratings"],
    summary="Get top 100 users leaderboard",
    parameters=[
        OpenApiParameter("start_date", str, description="Filter events from this date (YYYY-MM-DD)"),
        OpenApiParameter("end_date", str, description="Filter events up to this date (YYYY-MM-DD)"),
    ],
    responses={200: LeaderboardSerializer(many=True)},
)
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
