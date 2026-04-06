from django.contrib import admin
from .models import Category, FinancialRecord


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at"]
    search_fields = ["name"]


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "amount", "category", "date", "created_by", "is_deleted"]
    list_filter = ["type", "category", "is_deleted"]
    search_fields = ["notes", "category__name", "created_by__email"]
    ordering = ["-date"]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]

    def get_queryset(self, request):
        # Admin panel shows all records including soft-deleted
        return self.model.all_objects.all()
