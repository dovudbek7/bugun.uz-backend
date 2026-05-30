from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminUser
from apps.events.tasks import send_event_notification

from apps.common.permissions import IsOrganizer

from .models import OrganizerApplication, OrganizerProfile
from .serializers import (
    OrganizerApplicationCreateSerializer,
    OrganizerApplicationSerializer,
    OrganizerProfilePublicSerializer,
    OrganizerProfileSerializer,
)


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


class OrganizerProfileView(GenericAPIView):
    """Public: GET /api/organizer/{user_id}/profile/"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizerProfilePublicSerializer

    def get(self, request, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(pk=user_id, is_organizer=True).first()
        if not user:
            return Response({"detail": "Organizer not found."}, status=status.HTTP_404_NOT_FOUND)
        profile, _ = OrganizerProfile.objects.select_related("user").get_or_create(user=user)
        return Response(OrganizerProfilePublicSerializer(profile).data)


class OrganizerProfileMeView(GenericAPIView):
    """Organizer: GET/PUT /api/organizer/profile/me/"""
    permission_classes = [IsAuthenticated, IsOrganizer]
    serializer_class = OrganizerProfileSerializer

    def get(self, request):
        profile, _ = OrganizerProfile.objects.get_or_create(user=request.user)
        return Response(OrganizerProfileSerializer(profile).data)

    def put(self, request):
        profile, _ = OrganizerProfile.objects.get_or_create(user=request.user)
        serializer = OrganizerProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Profile updated"})
