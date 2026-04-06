"""
Management command to seed the database with:
- 1 Admin user
- 1 Analyst user
- 1 Viewer user
- Sample categories
- Sample financial records

Usage:
    python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from finance.models import Category, FinancialRecord
from datetime import date, timedelta
import random

User = get_user_model()


CATEGORIES = [
    ("Salary", "Monthly salary income"),
    ("Freelance", "Freelance project earnings"),
    ("Rent", "Monthly rent expense"),
    ("Food & Groceries", "Daily food and grocery expenses"),
    ("Utilities", "Electricity, water, internet bills"),
    ("Transport", "Fuel, cab, public transport"),
    ("Healthcare", "Medical bills and medicines"),
    ("Entertainment", "Movies, subscriptions, dining out"),
    ("Investments", "SIP, mutual funds, stocks"),
    ("Miscellaneous", "Other uncategorized expenses"),
]


class Command(BaseCommand):
    help = "Seed the database with initial users, categories, and financial records"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("🌱 Seeding database..."))

        # ── Users ──────────────────────────────────────────────
        admin, created = User.objects.get_or_create(
            email="admin@finance.com",
            defaults={"full_name": "Admin User", "role": "admin", "is_staff": True},
        )
        if created:
            admin.set_password("Admin@1234")
            admin.save()
            self.stdout.write(self.style.SUCCESS("  ✅ Admin user created   → admin@finance.com / Admin@1234"))
        else:
            self.stdout.write("  ℹ️  Admin user already exists")

        analyst, created = User.objects.get_or_create(
            email="analyst@finance.com",
            defaults={"full_name": "Analyst User", "role": "analyst"},
        )
        if created:
            analyst.set_password("Analyst@1234")
            analyst.save()
            self.stdout.write(self.style.SUCCESS("  ✅ Analyst user created → analyst@finance.com / Analyst@1234"))
        else:
            self.stdout.write("  ℹ️  Analyst user already exists")

        viewer, created = User.objects.get_or_create(
            email="viewer@finance.com",
            defaults={"full_name": "Viewer User", "role": "viewer"},
        )
        if created:
            viewer.set_password("Viewer@1234")
            viewer.save()
            self.stdout.write(self.style.SUCCESS("  ✅ Viewer user created  → viewer@finance.com / Viewer@1234"))
        else:
            self.stdout.write("  ℹ️  Viewer user already exists")

        # ── Categories ─────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n📂 Creating categories..."))
        category_objects = []
        for name, desc in CATEGORIES:
            cat, created = Category.objects.get_or_create(name=name, defaults={"description": desc})
            category_objects.append(cat)
            if created:
                self.stdout.write(f"  ✅ Category: {name}")

        # ── Financial Records ──────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n💰 Creating financial records..."))

        if FinancialRecord.objects.count() > 0:
            self.stdout.write("  ℹ️  Records already exist. Skipping.")
        else:
            income_categories = [c for c in category_objects if c.name in ("Salary", "Freelance", "Investments")]
            expense_categories = [c for c in category_objects if c.name not in ("Salary", "Freelance", "Investments")]

            records = []
            today = date.today()

            for i in range(60):  # 60 sample records
                record_date = today - timedelta(days=random.randint(0, 180))
                is_income = random.random() < 0.4  # 40% income, 60% expense

                records.append(FinancialRecord(
                    amount=round(random.uniform(100, 50000), 2),
                    type="income" if is_income else "expense",
                    category=random.choice(income_categories if is_income else expense_categories),
                    date=record_date,
                    notes=f"Sample {'income' if is_income else 'expense'} record #{i+1}",
                    created_by=admin,
                ))

            FinancialRecord.objects.bulk_create(records)
            self.stdout.write(self.style.SUCCESS(f"  ✅ Created {len(records)} financial records"))

        self.stdout.write(self.style.SUCCESS("\n✅ Seeding complete!\n"))
        self.stdout.write("👉 Login credentials:")
        self.stdout.write("   Admin   → admin@finance.com    / Admin@1234")
        self.stdout.write("   Analyst → analyst@finance.com  / Analyst@1234")
        self.stdout.write("   Viewer  → viewer@finance.com   / Viewer@1234")
