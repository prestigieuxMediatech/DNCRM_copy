from django.db import models

# Create your models here.


# payrolls/models.py

from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.db.models import UniqueConstraint

from employees.models import Employee


# ✅ ADDED: Callable for dynamic year
def current_year():
    return timezone.now().year


class Payroll(models.Model):
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("processing", "Processing"),
    ]

    MONTH_CHOICES = [
        ("January", "January"),
        ("February", "February"),
        ("March", "March"),
        ("April", "April"),
        ("May", "May"),
        ("June", "June"),
        ("July", "July"),
        ("August", "August"),
        ("September", "September"),
        ("October", "October"),
        ("November", "November"),
        ("December", "December"),
    ]

    # Employee
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="payrolls"
    )

    # Period
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year = models.PositiveIntegerField(default=current_year)
    # year = models.PositiveIntegerField(default=timezone.now().year)

    # Salary
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Deductions
    leave_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    other_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Net Salary (auto)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)

    # Payment
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")


    company_gst = models.CharField(max_length=20, blank=True)
    company_reg_no = models.CharField(max_length=30, blank=True)
    company_bank_name = models.CharField(max_length=100, blank=True)
    company_bank_account = models.CharField(max_length=50, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payroll"
        ordering = ["-year", "-month", "-created_at"]
        # unique_together = ["employee", "month", "year"]

         # ✅ ADDED: UniqueConstraint (modern Django way)
        constraints = [
            UniqueConstraint(
                fields=["employee", "month", "year"],
                name="unique_payroll_period"
            )
        ]




    def __str__(self):
        return f"{self.employee.full_name} - {self.month} {self.year}"

    def save(self, *args, **kwargs):
        self.net_salary = (
            Decimal(self.basic_salary)
            + Decimal(self.bonus)
            - Decimal(self.leave_deduction)
            - Decimal(self.other_deduction)
        )
        super().save(*args, **kwargs)

    @property
    def employee_name(self):
        return self.employee.full_name

    @property
    def employee_code(self):
        return self.employee.employee_code

    @property
    def designation(self):
        return self.employee.designation.title if self.employee.designation else ""

    @property
    def month_year(self):
        return f"{self.month} {self.year}"

    @property
    def annual_ctc(self):
        return self.employee.salary * 12

    @property
    def lpa(self):
        return float(self.annual_ctc) / 100000

    @property
    def lpa_display(self):
        return f"{self.lpa:.2f} LPA"