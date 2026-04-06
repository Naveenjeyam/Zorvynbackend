from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import FinancialRecord, Category
from .serializers import (
    FinancialRecordSerializer,
    FinancialRecordUpdateSerializer,
    CategorySerializer,
)
from .filters import FinancialRecordFilter
from core.permissions import IsAdmin, IsAnalystOrAdmin, IsAnyRole


# ─── Category Views ───────────────────────────────────────────────────────────

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/finance/categories/   — All roles can view
    POST /api/finance/categories/   — Admin only
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsAnyRole()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/finance/categories/<id>/  — All roles
    PUT    /api/finance/categories/<id>/  — Admin only
    DELETE /api/finance/categories/<id>/  — Admin only
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAnyRole()]
        return [IsAdmin()]


# ─── Financial Record Views ───────────────────────────────────────────────────

class FinancialRecordListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/finance/records/  — All roles: list with filters
    POST /api/finance/records/  — Admin only: create record
    """
    serializer_class = FinancialRecordSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = FinancialRecordFilter
    search_fields = ["notes", "category__name"]
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date"]

    def get_queryset(self):
        return FinancialRecord.objects.select_related("category", "created_by").all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsAnyRole()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class FinancialRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/finance/records/<id>/  — All roles
    PUT    /api/finance/records/<id>/  — Admin only
    PATCH  /api/finance/records/<id>/  — Admin only
    DELETE /api/finance/records/<id>/  — Admin only (soft delete)
    """
    def get_queryset(self):
        return FinancialRecord.objects.select_related("category", "created_by").all()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return FinancialRecordUpdateSerializer
        return FinancialRecordSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAnyRole()]
        return [IsAdmin()]

    def destroy(self, request, *args, **kwargs):
        record = self.get_object()
        record.soft_delete()
        return Response(
            {"message": "Record has been deleted successfully."},
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            # Return full record data after update
            return Response(FinancialRecordSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
