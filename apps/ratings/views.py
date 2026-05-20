from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import mixins, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

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
        return (
            User.objects.annotate(rates_count=Count("ratings_received"))
            .filter(total_attended__gt=0)
            .order_by("-total_attended", "-rating", "-rates_count")[:100]
        )
