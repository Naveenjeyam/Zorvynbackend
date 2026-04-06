from django.urls import path
from .views import (
    OverviewSummaryView,
    CategoryBreakdownView,
    MonthlyTrendView,
    WeeklyTrendView,
    RecentActivityView,
)

urlpatterns = [
    path("summary/", OverviewSummaryView.as_view(), name="dashboard-summary"),
    path("category-breakdown/", CategoryBreakdownView.as_view(), name="category-breakdown"),
    path("monthly-trend/", MonthlyTrendView.as_view(), name="monthly-trend"),
    path("weekly-trend/", WeeklyTrendView.as_view(), name="weekly-trend"),
    path("recent-activity/", RecentActivityView.as_view(), name="recent-activity"),
]
