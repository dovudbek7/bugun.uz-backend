from django.contrib.auth import get_user_model
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.attendance.models import Attendance

from .serializers import (
    HistorySerializer,
    OnboardingSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    TelegramLoginSerializer,
    TelegramWebAppLoginSerializer,
)


User = get_user_model()


class TelegramLoginView(GenericAPIView):
    serializer_class = TelegramLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())


class TelegramWebAppLoginView(GenericAPIView):
    serializer_class = TelegramWebAppLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())


class OnboardingView(GenericAPIView):
    serializer_class = OnboardingSerializer

    def post(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Profile completed"})


class ProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.prefetch_related("user_interests__interest", "user_achievements__achievement")
    serializer_class = ProfileSerializer

    @action(detail=False, methods=["get", "put"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            return Response(ProfileSerializer(request.user, context=self.get_serializer_context()).data)
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Profile updated"})

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        data = self.get_serializer(user).data
        if not data["show_telegram"]:
            data["telegram_username"] = None
        if request.user.id != user.id:
            data.pop("phone_number", None)
        return Response(data)


class HistoryView(ListAPIView):
    serializer_class = HistorySerializer
    pagination_class = None

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Attendance.objects.none()
        return Attendance.objects.filter(user=self.request.user).select_related("event").order_by("-event__event_date")
