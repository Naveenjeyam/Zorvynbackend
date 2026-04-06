from rest_framework import serializers
from .models import FinancialRecord, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class FinancialRecordSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = FinancialRecord
        fields = [
            "id",
            "amount",
            "type",
            "category",
            "category_name",
            "date",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_name", "created_at", "updated_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        return value

    def validate_type(self, value):
        if value not in ("income", "expense"):
            raise serializers.ValidationError("Type must be 'income' or 'expense'.")
        return value


class FinancialRecordUpdateSerializer(serializers.ModelSerializer):
    """Separate serializer for partial updates — all fields optional."""
    class Meta:
        model = FinancialRecord
        fields = ["amount", "type", "category", "date", "notes"]

    def validate_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        return value
