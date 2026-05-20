from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.common.permissions import IsAdminUser
from apps.events.tasks import send_event_notification

from .models import OrganizerApplication
from .serializers import OrganizerApplicationCreateSerializer, OrganizerApplicationSerializer


class OrganizerRequestView(GenericAPIView):
    def get_serializer_class(self):
        return OrganizerApplicationCreateSerializer

    def get(self, request):
        application = OrganizerApplication.objects.filter(user=request.user).order_by("-created_at").first()
        return Response({"status": application.status if application else None})

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Request sent"}, status=status.HTTP_201_CREATED)


class AdminOrganizerRequestViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = OrganizerApplication.objects.select_related("user")
    serializer_class = OrganizerApplicationSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        application = self.get_object()
        application.status = OrganizerApplication.STATUS_APPROVED
        application.save(update_fields=["status"])
        user = application.user
        user.is_organizer = True
        user.save(update_fields=["is_organizer", "updated_at"])
        send_event_notification.delay(user.id, "Your organizer request has been approved.")
        return Response({"message": "Organizer approved"})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        application = self.get_object()
        application.status = OrganizerApplication.STATUS_REJECTED
        application.save(update_fields=["status"])
        send_event_notification.delay(application.user_id, "Your organizer request has been rejected.")
        return Response({"message": "Organizer rejected"})
