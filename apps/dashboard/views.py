from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Max
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from apps.accounts.models import User
from apps.attendance.models import Attendance
from apps.categories.models import Category
from apps.events.models import Event
from apps.reports.models import Report


@method_decorator(staff_member_required, name="dispatch")
class StatisticsView(View):
    template_name = "dashboard/statistics.html"

    def get(self, request):
        today = timezone.localdate()

        user_stats = {
            "total": User.objects.count(),
            "today": User.objects.filter(created_at__date=today).count(),
            "organizers": User.objects.filter(is_organizer=True).count(),
        }

        event_stats = {
            "total": Event.objects.count(),
            "today": Event.objects.filter(event_date=today).count(),
            "upcoming": Event.objects.filter(status=Event.STATUS_UPCOMING).count(),
            "completed": Event.objects.filter(status=Event.STATUS_COMPLETED).count(),
            "cancelled": Event.objects.filter(status=Event.STATUS_CANCELLED).count(),
            "draft": Event.objects.filter(is_draft=True).count(),
        }

        attendance_stats = {
            "total_joined": Attendance.objects.filter(status__in=[Attendance.STATUS_JOINED, Attendance.STATUS_ATTENDED]).count(),
            "total_attended": Attendance.objects.filter(status=Attendance.STATUS_ATTENDED).count(),
        }

        popular_event = (
            Event.objects.annotate(attendee_count=Count("attendances"))
            .order_by("-attendee_count")
            .first()
        )

        top_category = (
            Category.objects.annotate(event_count=Count("events"))
            .order_by("-event_count")
            .first()
        )

        category_stats = {
            "total": Category.objects.count(),
            "top": top_category,
        }

        report_stats = {
            "total": Report.objects.count(),
        }

        recent_events = (
            Event.objects.select_related("category", "organizer", "location")
            .order_by("-created_at")[:5]
        )

        context = {
            "user_stats": user_stats,
            "event_stats": event_stats,
            "attendance_stats": attendance_stats,
            "popular_event": popular_event,
            "category_stats": category_stats,
            "report_stats": report_stats,
            "recent_events": recent_events,
            "today": today,
        }
        return render(request, self.template_name, context)


@method_decorator(staff_member_required, name="dispatch")
class ReportsView(View):
    template_name = "dashboard/reports.html"

    def get(self, request):
        reports = (
            Report.objects.select_related("reporter", "target_user")
            .order_by("-created_at")
        )
        context = {"reports": reports, "total": reports.count()}
        return render(request, self.template_name, context)
