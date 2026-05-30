from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.attendance.models import Attendance

from .serializers import (
    HistorySerializer,
    OnboardingSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    SubmitPhoneSerializer,
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


class SubmitPhoneView(GenericAPIView):
    serializer_class = SubmitPhoneSerializer
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


class DevLoginView(GenericAPIView):
    """DEBUG-only: returns JWT tokens for any mock user — never enabled in production."""
    permission_classes = [AllowAny]

    def get(self, request):
        if not settings.DEBUG:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        user_id = request.query_params.get("user_id", 1)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = User.objects.filter(full_name__isnull=False).exclude(full_name="").first()
            if not user:
                return Response({"detail": "No mock users found. Run: manage.py generate_mock"}, status=400)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id,
            "full_name": user.full_name,
        })


class HistoryView(ListAPIView):
    serializer_class = HistorySerializer
    pagination_class = None

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Attendance.objects.none()
        return Attendance.objects.filter(user=self.request.user).select_related("event").order_by("-event__event_date")
