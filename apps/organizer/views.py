from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminUser, IsOrganizer
from apps.events.tasks import send_event_notification

from .models import OrganizerApplication, OrganizerProfile
from .serializers import (
    OrganizerApplicationCreateSerializer,
    OrganizerApplicationSerializer,
    OrganizerProfilePublicSerializer,
    OrganizerProfileSerializer,
)

_MSG = inline_serializer("OrgMsgResponse", fields={"message": serializers.CharField()})
_STATUS_RESPONSE = inline_serializer("OrganizerStatusResponse", fields={
    "status": serializers.ChoiceField(choices=["pending", "approved", "rejected", None], allow_null=True),
})


@extend_schema(tags=["Organizer"])
class OrganizerRequestView(GenericAPIView):
    def get_serializer_class(self):
        return OrganizerApplicationCreateSerializer

    @extend_schema(summary="Get own organizer application status", responses={200: _STATUS_RESPONSE})
    def get(self, request):
        application = OrganizerApplication.objects.filter(user=request.user).order_by("-created_at").first()
        return Response({"status": application.status if application else None})

    @extend_schema(
        summary="Submit organizer application",
        responses={201: inline_serializer("OrganizerRequestCreated", fields={"message": serializers.CharField()})},
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Request sent"}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Admin"])
class AdminOrganizerRequestViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = OrganizerApplication.objects.select_related("user")
    serializer_class = OrganizerApplicationSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(summary="List all organizer applications")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Approve organizer application",
        request=None,
        responses={200: inline_serializer("ApproveResponse", fields={"message": serializers.CharField()})},
    )
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

    @extend_schema(
        summary="Reject organizer application",
        request=None,
        responses={200: inline_serializer("RejectResponse", fields={"message": serializers.CharField()})},
    )
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        application = self.get_object()
        application.status = OrganizerApplication.STATUS_REJECTED
        application.save(update_fields=["status"])
        send_event_notification.delay(application.user_id, "Your organizer request has been rejected.")
        return Response({"message": "Organizer rejected"})


@extend_schema(tags=["Organizer"])
class OrganizerProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizerProfilePublicSerializer

    @extend_schema(
        summary="Get public organizer profile",
        responses={200: OrganizerProfilePublicSerializer, 404: OpenApiResponse(description="Organizer not found")},
    )
    def get(self, request, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(pk=user_id, is_organizer=True).first()
        if not user:
            return Response({"detail": "Organizer not found."}, status=status.HTTP_404_NOT_FOUND)
        profile, _ = OrganizerProfile.objects.select_related("user").get_or_create(user=user)
        return Response(OrganizerProfilePublicSerializer(profile).data)


@extend_schema(tags=["Organizer"])
class OrganizerProfileMeView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsOrganizer]
    serializer_class = OrganizerProfileSerializer

    @extend_schema(summary="Get own organizer profile", responses={200: OrganizerProfileSerializer})
    def get(self, request):
        profile, _ = OrganizerProfile.objects.get_or_create(user=request.user)
        return Response(OrganizerProfileSerializer(profile).data)

    @extend_schema(
        summary="Update own organizer profile",
        responses={200: inline_serializer("OrganizerProfileUpdated", fields={"message": serializers.CharField()})},
    )
    def put(self, request):
        profile, _ = OrganizerProfile.objects.get_or_create(user=request.user)
        serializer = OrganizerProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Profile updated"})
