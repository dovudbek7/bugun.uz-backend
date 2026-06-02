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
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Profile updated"})


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

    @action(detail=True, methods=["get", "post"], url_path="follow")
    def follow(self, request, pk=None):
        from .models import UserFollow
        target = self.get_object()
        if target.id == request.user.id:
            return Response({"detail": "Cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        if request.method == "GET":
            following = UserFollow.objects.filter(follower=request.user, following=target).exists()
            return Response({"following": following})
        existing = UserFollow.objects.filter(follower=request.user, following=target).first()
        if existing:
            existing.delete()
            return Response({"following": False})
        UserFollow.objects.create(follower=request.user, following=target)
        return Response({"following": True}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="me/followers")
    def followers_count(self, request):
        from .models import UserFollow
        followers = UserFollow.objects.filter(following=request.user).count()
        following = UserFollow.objects.filter(follower=request.user).count()
        return Response({"followers": followers, "following": following})

    @action(detail=False, methods=["get"], url_path="me/stats")
    def stats(self, request):
        from django.db.models import Count
        from django.utils import timezone as tz
        user = request.user

        total = Attendance.objects.filter(user=user, status__in=[Attendance.STATUS_JOINED, Attendance.STATUS_ATTENDED]).count()

        top_cat_qs = (
            Attendance.objects.filter(user=user, status__in=[Attendance.STATUS_JOINED, Attendance.STATUS_ATTENDED])
            .values("event__category__id", "event__category__title")
            .annotate(count=Count("id"))
            .order_by("-count")
            .first()
        )
        top_category = None
        if top_cat_qs:
            top_category = {
                "id": top_cat_qs["event__category__id"],
                "title": top_cat_qs["event__category__title"],
                "count": top_cat_qs["count"],
            }

        months = max((tz.now() - user.date_joined).days / 30, 1)
        avg_per_month = round(total / months, 1)

        attended_event_ids = Attendance.objects.filter(
            user=user, status=Attendance.STATUS_ATTENDED
        ).values_list("event_id", flat=True)
        co_attendee_qs = (
            Attendance.objects.filter(event_id__in=attended_event_ids, status=Attendance.STATUS_ATTENDED)
            .exclude(user=user)
            .values("user_id", "user__full_name")
            .annotate(count=Count("id"))
            .order_by("-count")
            .first()
        )
        favorite_co_attendee = None
        if co_attendee_qs:
            favorite_co_attendee = {
                "id": co_attendee_qs["user_id"],
                "full_name": co_attendee_qs["user__full_name"],
                "count": co_attendee_qs["count"],
            }

        return Response({
            "total_events": total,
            "top_category": top_category,
            "avg_per_month": avg_per_month,
            "favorite_co_attendee": favorite_co_attendee,
        })


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
