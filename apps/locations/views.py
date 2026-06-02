from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, serializers, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.common.permissions import IsOrganizer

from .models import Location
from .serializers import LocationSerializer


@extend_schema(tags=["Locations"])
class LocationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsOrganizer()]
        return [AllowAny()]

    @extend_schema(
        summary="Create location (organizer only)",
        responses={201: inline_serializer("LocationCreated", fields={
            "message": serializers.CharField(),
            "location": LocationSerializer(),
        })},
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {"message": "Location created", "location": response.data}
        return response
