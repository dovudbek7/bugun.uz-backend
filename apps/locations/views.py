from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.common.permissions import IsOrganizer

from .models import Location
from .serializers import LocationSerializer


class LocationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsOrganizer()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {"message": "Location created", "location": response.data}
        return response
