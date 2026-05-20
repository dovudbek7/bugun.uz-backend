from django.urls import path

from .views import ReportsView, StatisticsView

urlpatterns = [
    path("statistics/", StatisticsView.as_view(), name="dashboard-statistics"),
    path("reports/", ReportsView.as_view(), name="dashboard-reports"),
]
