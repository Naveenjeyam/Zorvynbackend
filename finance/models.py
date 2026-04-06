from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SoftDeleteManager(models.Manager):
    """Returns only non-deleted records by default."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Category(models.Model):
    """
    Predefined categories for financial records.
    e.g. Salary, Rent, Food, Utilities, Freelance, etc.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class FinancialRecord(models.Model):
    """
    A single financial transaction entry.

    Fields:
      - amount       : Decimal value (always positive; type decides income/expense)
      - type         : 'income' or 'expense'
      - category     : FK to Category
      - date         : The actual date of the transaction
      - notes        : Optional description
      - created_by   : FK to the User who created this record
      - is_deleted   : Soft delete flag
    """

    class TransactionType(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="records",
    )
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="financial_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft delete fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Managers
    objects = SoftDeleteManager()           # default: excludes deleted
    all_objects = models.Manager()          # includes deleted (admin use)

    class Meta:
        db_table = "financial_records"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.type.upper()} | {self.amount} | {self.date}"

    def soft_delete(self, commit=True):
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if commit:
            self.save(update_fields=["is_deleted", "deleted_at"])
