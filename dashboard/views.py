from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta

from finance.models import FinancialRecord
from core.permissions import IsAnyRole, IsAnalystOrAdmin


class OverviewSummaryView(APIView):
    """
    GET /api/dashboard/summary/
    Returns total income, total expenses, and net balance.
    Access: All roles (Viewer, Analyst, Admin)
    """
    permission_classes = [IsAnyRole]

    def get(self, request):
        queryset = FinancialRecord.objects.all()

        # Optional: filter by year
        year = request.query_params.get("year")
        if year:
            queryset = queryset.filter(date__year=year)

        totals = queryset.aggregate(
            total_income=Sum("amount", filter=Q(type="income")),
            total_expenses=Sum("amount", filter=Q(type="expense")),
            total_records=Count("id"),
        )

        total_income = totals["total_income"] or 0
        total_expenses = totals["total_expenses"] or 0
        net_balance = total_income - total_expenses

        return Response(
            {
                "total_income": round(float(total_income), 2),
                "total_expenses": round(float(total_expenses), 2),
                "net_balance": round(float(net_balance), 2),
                "total_records": totals["total_records"],
                "filter": {"year": year} if year else "all time",
            }
        )


class CategoryBreakdownView(APIView):
    """
    GET /api/dashboard/category-breakdown/
    Returns totals grouped by category.
    Access: Analyst and Admin
    """
    permission_classes = [IsAnalystOrAdmin]

    def get(self, request):
        transaction_type = request.query_params.get("type")  # 'income' or 'expense'
        year = request.query_params.get("year")
        month = request.query_params.get("month")

        queryset = FinancialRecord.objects.all()

        if transaction_type in ("income", "expense"):
            queryset = queryset.filter(type=transaction_type)
        if year:
            queryset = queryset.filter(date__year=year)
        if month:
            queryset = queryset.filter(date__month=month)

        breakdown = (
            queryset
            .values("category__id", "category__name")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )

        result = [
            {
                "category_id": item["category__id"],
                "category_name": item["category__name"] or "Uncategorized",
                "total": round(float(item["total"]), 2),
                "record_count": item["count"],
            }
            for item in breakdown
        ]

        return Response({"breakdown": result, "filters_applied": {"type": transaction_type, "year": year, "month": month}})


class MonthlyTrendView(APIView):
    """
    GET /api/dashboard/monthly-trend/
    Returns income and expense totals grouped by month.
    Access: Analyst and Admin
    """
    permission_classes = [IsAnalystOrAdmin]

    def get(self, request):
        year = request.query_params.get("year", timezone.now().year)

        queryset = FinancialRecord.objects.filter(date__year=year)

        monthly = (
            queryset
            .annotate(month=TruncMonth("date"))
            .values("month", "type")
            .annotate(total=Sum("amount"))
            .order_by("month", "type")
        )

        # Organize into a clean month-by-month structure
        trend_map = {}
        for entry in monthly:
            month_key = entry["month"].strftime("%Y-%m")
            if month_key not in trend_map:
                trend_map[month_key] = {"month": month_key, "income": 0.0, "expense": 0.0}
            trend_map[month_key][entry["type"]] = round(float(entry["total"]), 2)

        # Add net balance per month
        trend = []
        for month_key, data in sorted(trend_map.items()):
            data["net"] = round(data["income"] - data["expense"], 2)
            trend.append(data)

        return Response({"year": year, "monthly_trend": trend})


class WeeklyTrendView(APIView):
    """
    GET /api/dashboard/weekly-trend/
    Returns income and expense totals for the last 8 weeks.
    Access: Analyst and Admin
    """
    permission_classes = [IsAnalystOrAdmin]

    def get(self, request):
        eight_weeks_ago = timezone.now().date() - timedelta(weeks=8)

        queryset = FinancialRecord.objects.filter(date__gte=eight_weeks_ago)

        weekly = (
            queryset
            .annotate(week=TruncWeek("date"))
            .values("week", "type")
            .annotate(total=Sum("amount"))
            .order_by("week", "type")
        )

        trend_map = {}
        for entry in weekly:
            week_key = entry["week"].strftime("%Y-%m-%d")
            if week_key not in trend_map:
                trend_map[week_key] = {"week_starting": week_key, "income": 0.0, "expense": 0.0}
            trend_map[week_key][entry["type"]] = round(float(entry["total"]), 2)

        trend = []
        for week_key, data in sorted(trend_map.items()):
            data["net"] = round(data["income"] - data["expense"], 2)
            trend.append(data)

        return Response({"weekly_trend": trend})


class RecentActivityView(APIView):
    """
    GET /api/dashboard/recent-activity/
    Returns the latest 10 transactions.
    Access: All roles
    """
    permission_classes = [IsAnyRole]

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        limit = min(limit, 50)  # cap at 50

        records = (
            FinancialRecord.objects
            .select_related("category", "created_by")
            .order_by("-date", "-created_at")[:limit]
        )

        data = [
            {
                "id": r.id,
                "amount": float(r.amount),
                "type": r.type,
                "category": r.category.name if r.category else "Uncategorized",
                "date": r.date,
                "notes": r.notes,
                "created_by": r.created_by.full_name,
            }
            for r in records
        ]

        return Response({"recent_activity": data, "count": len(data)})
