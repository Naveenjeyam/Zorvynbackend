from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from core import views

schema_view = get_schema_view(
    openapi.Info(
        title="Finance Dashboard API",
        default_version="v1",
        description="Backend API for the Finance Dashboard System",
        contact=openapi.Contact(email="admin@finance.com"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.home, name="home"),
    # Auth endpoints
    path("api/auth/", include("core.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Finance endpoints
    path("api/finance/", include("finance.urls")),

    # Dashboard endpoints
    path("api/dashboard/", include("dashboard.urls")),

    # Swagger docs
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
]
