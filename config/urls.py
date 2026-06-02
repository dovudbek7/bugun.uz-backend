from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import DevLoginView, HistoryView, OnboardingView, ProfileViewSet, SubmitPhoneView, TelegramLoginView, TelegramWebAppLoginView
from apps.achievements.views import MyAchievementsView
from apps.categories.views import CategoryViewSet
from apps.events.views import EventViewSet, MapEventsView
from apps.interests.views import InterestViewSet
from apps.locations.views import LocationViewSet
from apps.organizer.views import AdminOrganizerRequestViewSet, OrganizerProfileMeView, OrganizerProfileView, OrganizerRequestView
from apps.ratings.views import LeaderboardView, RatingViewSet
from apps.reports.views import AdminReportViewSet, ReportViewSet


router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("interests", InterestViewSet, basename="interest")
router.register("locations", LocationViewSet, basename="location")
router.register("events", EventViewSet, basename="event")
router.register("ratings", RatingViewSet, basename="rating")
router.register("reports", ReportViewSet, basename="report")
router.register("admin/organizer-requests", AdminOrganizerRequestViewSet, basename="admin-organizer-request")
router.register("admin/reports", AdminReportViewSet, basename="admin-report")
router.register("profile", ProfileViewSet, basename="profile")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("apps.dashboard.urls")),
    path("api/auth/telegram/", TelegramLoginView.as_view(), name="telegram-login"),
    path("api/auth/telegram-webapp/", TelegramWebAppLoginView.as_view(), name="telegram-webapp-login"),
    path("api/profile/change/", OnboardingView.as_view(), name="profile-change"),
    path("api/auth/submit-phone/", SubmitPhoneView.as_view(), name="submit-phone"),
    path("api/auth/dev-login/", DevLoginView.as_view(), name="dev-login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/organizer/request/", OrganizerRequestView.as_view(), name="organizer-request"),
    path("api/organizer/profile/me/", OrganizerProfileMeView.as_view(), name="organizer-profile-me"),
    path("api/organizer/<int:user_id>/profile/", OrganizerProfileView.as_view(), name="organizer-profile"),
    path("api/leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("api/achievements/me/", MyAchievementsView.as_view(), name="my-achievements"),
    path("api/history/me/", HistoryView.as_view(), name="my-history"),
    path("api/maps/", MapEventsView.as_view(), name="maps"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
