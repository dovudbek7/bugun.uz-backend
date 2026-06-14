from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attendance.models import Attendance, WaitingList
from apps.attendance.services import join_event, leave_event, promote_all_waiting_users
from apps.achievements.services import award_joined_achievements
from apps.common.permissions import IsOrganizer, IsOrganizerOwnerOrReadOnly
from apps.events.tasks import notify_category_subscribers, send_attendance_notification, send_event_notification, send_new_event_notification, translate_event

from .models import Event
from .serializers import (
    EventDetailSerializer,
    EventListSerializer,
    EventMapSerializer,
    EventSearchSerializer,
    EventWriteSerializer,
    ParticipantSerializer,
    WaitingListSerializer,
)

_MSG_RESPONSE = inline_serializer("EventMsgResponse", fields={"message": serializers.CharField()})

_JOIN_STATUS_RESPONSE = inline_serializer("JoinStatusResponse", fields={
    "status": serializers.ChoiceField(choices=["not_joined", "waiting", "joined", "attended", "cancelled"]),
})

_WAITING_POSITION_RESPONSE = inline_serializer("WaitingPositionResponse", fields={
    "position": serializers.IntegerField(allow_null=True),
    "total": serializers.IntegerField(),
})

_ANALYTICS_RESPONSE = inline_serializer("EventAnalyticsResponse", fields={
    "total_seats": serializers.IntegerField(),
    "joined_count": serializers.IntegerField(),
    "attended_count": serializers.IntegerField(),
    "cancelled_count": serializers.IntegerField(),
    "waiting_count": serializers.IntegerField(),
    "fill_rate": serializers.IntegerField(),
    "attendance_rate": serializers.IntegerField(),
})


@extend_schema(tags=["Events"])
class EventViewSet(viewsets.ModelViewSet):
    filterset_fields = ("category", "status", "is_draft")

    def get_queryset(self):
        queryset = Event.objects.select_related("category", "location", "organizer").prefetch_related("attendances__user")
        if self.action in {"list", "retrieve", "search"} and not self.request.user.is_staff:
            queryset = queryset.filter(is_draft=False)
        category = self.request.query_params.get("category")
        status_value = self.request.query_params.get("status")
        draft = self.request.query_params.get("draft")
        today = self.request.query_params.get("today")
        if category:
            queryset = queryset.filter(category_id=category)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if draft is not None:
            queryset = queryset.filter(is_draft=draft.lower() == "true")
        if today == "true":
            queryset = queryset.filter(event_date=timezone.localdate())
        return queryset

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return EventWriteSerializer
        if self.action == "search":
            return EventSearchSerializer
        if self.action == "retrieve":
            return EventDetailSerializer
        return EventListSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticated()]
        if self.action in {"create"}:
            return [IsAuthenticated(), IsOrganizer()]
        if self.action in {"update", "partial_update", "destroy"}:
            return [IsAuthenticated(), IsOrganizerOwnerOrReadOnly()]
        if self.action in {"participants", "waiting_list", "mark_attendance"}:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def _require_event_manager(self, event):
        if not (self.request.user.is_staff or event.organizer_id == self.request.user.id):
            return Response({"detail": "Only the event organizer can manage this event."}, status=status.HTTP_403_FORBIDDEN)
        return None

    @extend_schema(summary="Create event", responses={201: _MSG_RESPONSE})
    def create(self, request, *args, **kwargs):
        from apps.accounts.models import UserFollow
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        translate_event.delay(event.pk)
        follower_ids = UserFollow.objects.filter(following=request.user).values_list("follower_id", flat=True)
        for fid in follower_ids:
            send_new_event_notification.delay(fid, event.pk)
        notify_category_subscribers.delay(event.pk)
        return Response({"message": "Event created"}, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Update event", responses={200: _MSG_RESPONSE})
    def update(self, request, *args, **kwargs):
        event = self.get_object()
        old_seats = event.total_seats
        old_description = event.description
        serializer = self.get_serializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        if event.total_seats > old_seats:
            promote_all_waiting_users(event)
        if event.description != old_description:
            event.translation_status = Event.TRANSLATION_PENDING
            event.save(update_fields=["translation_status", "updated_at"])
            translate_event.delay(event.pk)
        return Response({"message": "Event updated"})

    @extend_schema(summary="Delete (cancel) event", responses={200: _MSG_RESPONSE})
    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        reason = request.data.get("reason", "")
        event.status = Event.STATUS_CANCELLED
        event.cancellation_reason = reason
        event.save(update_fields=["status", "cancellation_reason", "updated_at"])
        participants = Attendance.objects.filter(event=event, status__in=[Attendance.STATUS_JOINED, Attendance.STATUS_ATTENDED])
        for attendance in participants.only("user_id"):
            send_attendance_notification.delay(attendance.user_id, event.pk, "org_cancelled")
        return Response({"message": "Event deleted"})

    @extend_schema(
        summary="Cancel event (organizer) or leave event (user)",
        request=inline_serializer("CancelRequest", fields={"reason": serializers.CharField(required=False, allow_blank=True)}),
        responses={200: OpenApiResponse(description="Cancelled successfully")},
    )
    @action(detail=True, methods=["post", "patch"], url_path="cancel", permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        event = self.get_object()
        is_owner = request.user.is_staff or event.organizer_id == request.user.id

        if is_owner:
            if event.status == Event.STATUS_CANCELLED:
                return Response({"detail": "Event is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)
            reason = request.data.get("reason", "")
            event.status = Event.STATUS_CANCELLED
            event.cancellation_reason = reason
            event.save(update_fields=["status", "cancellation_reason", "updated_at"])
            participants = Attendance.objects.filter(
                event=event, status__in=[Attendance.STATUS_JOINED, Attendance.STATUS_ATTENDED]
            )
            for attendance in participants.only("user_id"):
                send_attendance_notification.delay(attendance.user_id, event.pk, "org_cancelled")
            return Response(EventDetailSerializer(event).data)

        message = leave_event(request.user, event)
        return Response({"message": message})

    @extend_schema(summary="List today's upcoming events", responses={200: EventListSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="today", permission_classes=[IsAuthenticated])
    def today(self, request):
        queryset = self.get_queryset().filter(event_date=timezone.localdate(), status=Event.STATUS_UPCOMING)
        return Response(EventListSerializer(queryset, many=True).data)

    @extend_schema(
        summary="Check user's join status for an event",
        parameters=[OpenApiParameter("user_id", int, description="Defaults to current user")],
        responses={200: _JOIN_STATUS_RESPONSE},
    )
    @action(detail=True, methods=["get"], url_path="join-status", permission_classes=[IsAuthenticated])
    def join_status(self, request, pk=None):
        event = self.get_object()
        user_id = request.query_params.get("user_id", request.user.id)
        in_waiting = WaitingList.objects.filter(event=event, user_id=user_id).exists()
        if in_waiting:
            return Response({"status": "waiting"})
        attendance = Attendance.objects.filter(event=event, user_id=user_id).exclude(status=Attendance.STATUS_CANCELLED).first()
        if attendance:
            return Response({"status": attendance.status})
        return Response({"status": "not_joined"})

    @extend_schema(
        summary="Get event by deep link ref",
        parameters=[OpenApiParameter("ref", str, description="Deep link ref, e.g. event_42")],
        responses={200: EventDetailSerializer, 400: OpenApiResponse(description="Invalid ref"), 404: OpenApiResponse(description="Not found")},
    )
    @action(detail=False, methods=["get"], url_path="by-deep-link", permission_classes=[IsAuthenticated])
    def by_deep_link(self, request):
        ref = request.query_params.get("ref", "")
        if not ref.startswith("event_"):
            return Response({"detail": "invalid ref"}, status=status.HTTP_400_BAD_REQUEST)
        event_id = ref.replace("event_", "")
        try:
            event = Event.objects.select_related("category", "location", "organizer").prefetch_related("attendances__user").get(pk=event_id, is_draft=False)
        except Event.DoesNotExist:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(EventDetailSerializer(event).data)

    @extend_schema(
        summary="Search events",
        parameters=[OpenApiParameter("q", str, description="Search query (title, category, organizer, location)")],
        responses={200: EventSearchSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="search", permission_classes=[IsAuthenticated])
    def search(self, request):
        q = request.query_params.get("q", "").strip()
        queryset = self.get_queryset()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(category__title__icontains=q)
                | Q(organizer__full_name__icontains=q)
                | Q(location__title__icontains=q)
                | Q(location__address__icontains=q)
            ).distinct()
        return Response(EventSearchSerializer(queryset[:50], many=True).data)

    @extend_schema(summary="Join event", responses={200: _MSG_RESPONSE})
    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        message = join_event(request.user, self.get_object())
        return Response({"message": message})

    @extend_schema(summary="Leave event", responses={200: _MSG_RESPONSE})
    @action(detail=True, methods=["post"])
    def leave(self, request, pk=None):
        message = leave_event(request.user, self.get_object())
        return Response({"message": message})

    @extend_schema(summary="List event participants (organizer only)", responses={200: ParticipantSerializer(many=True)})
    @action(detail=True, methods=["get"])
    def participants(self, request, pk=None):
        event = self.get_object()
        forbidden = self._require_event_manager(event)
        if forbidden:
            return forbidden
        items = Attendance.objects.filter(event=event).exclude(status=Attendance.STATUS_CANCELLED).select_related("user")
        return Response(ParticipantSerializer(items, many=True).data)

    @extend_schema(summary="List waiting list (organizer only)", responses={200: WaitingListSerializer(many=True)})
    @action(detail=True, methods=["get"], url_path="waiting-list")
    def waiting_list(self, request, pk=None):
        event = self.get_object()
        forbidden = self._require_event_manager(event)
        if forbidden:
            return forbidden
        items = WaitingList.objects.filter(event=event).select_related("user")
        return Response(WaitingListSerializer(items, many=True).data)

    @extend_schema(summary="Get current user's position in waiting list", responses={200: _WAITING_POSITION_RESPONSE})
    @action(detail=True, methods=["get"], url_path="waiting-list/position")
    def waiting_list_position(self, request, pk=None):
        event = self.get_object()
        entry = WaitingList.objects.filter(event=event, user=request.user).first()
        if not entry:
            return Response({"position": None, "total": WaitingList.objects.filter(event=event).count()})
        position = WaitingList.objects.filter(event=event, created_at__lt=entry.created_at).count() + 1
        total = WaitingList.objects.filter(event=event).count()
        return Response({"position": position, "total": total})

    @extend_schema(summary="Get event analytics (organizer only)", responses={200: _ANALYTICS_RESPONSE})
    @action(detail=True, methods=["get"], url_path="analytics")
    def analytics(self, request, pk=None):
        event = self.get_object()
        forbidden = self._require_event_manager(event)
        if forbidden:
            return forbidden
        from django.db.models import Count
        counts = Attendance.objects.filter(event=event).aggregate(
            joined=Count("id", filter=Q(status=Attendance.STATUS_JOINED)),
            attended=Count("id", filter=Q(status=Attendance.STATUS_ATTENDED)),
            cancelled=Count("id", filter=Q(status=Attendance.STATUS_CANCELLED)),
        )
        joined = counts["joined"]
        attended = counts["attended"]
        waiting = event.waiting_list.count()
        fill_rate = round(joined / event.total_seats * 100) if event.total_seats else 0
        attendance_rate = round(attended / joined * 100) if joined else 0
        return Response({
            "total_seats": event.total_seats,
            "joined_count": joined,
            "attended_count": attended,
            "cancelled_count": counts["cancelled"],
            "waiting_count": waiting,
            "fill_rate": fill_rate,
            "attendance_rate": attendance_rate,
        })

    @extend_schema(
        summary="Mark user as attended",
        request=None,
        responses={200: _MSG_RESPONSE, 404: OpenApiResponse(description="Joined attendance not found")},
    )
    @action(detail=True, methods=["post"], url_path=r"attendance/(?P<user_id>\d+)")
    def mark_attendance(self, request, pk=None, user_id=None):
        event = self.get_object()
        forbidden = self._require_event_manager(event)
        if forbidden:
            return forbidden
        attendance = Attendance.objects.filter(event=event, user_id=user_id, status=Attendance.STATUS_JOINED).first()
        if not attendance:
            return Response({"detail": "Joined attendance not found."}, status=status.HTTP_404_NOT_FOUND)
        attendance.status = Attendance.STATUS_ATTENDED
        attendance.save(update_fields=["status"])
        user = attendance.user
        user.total_attended = Attendance.objects.filter(user=user, status=Attendance.STATUS_ATTENDED).count()
        user.save(update_fields=["total_attended", "updated_at"])
        award_joined_achievements(user)
        return Response({"message": "User marked as attended"})


@extend_schema(tags=["Events"], summary="List events with map coordinates")
class MapEventsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventMapSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            Event.objects.select_related("category", "location")
            .filter(status=Event.STATUS_UPCOMING, is_draft=False)
            .order_by("event_date", "event_time")
        )
