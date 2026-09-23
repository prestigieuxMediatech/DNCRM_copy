from django.contrib import admin

# Register your models here.

# payrolls/admin.py

from django.contrib import admin
from .models import Payroll


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = [
        "employee_code", "employee_name", "month_year",
        "basic_salary", "leave_deduction", "net_salary",
        "status", "payment_date"
    ]
    list_filter = ["status", "month", "year"]
    search_fields = ["employee__first_name", "employee__last_name", "employee__employee_code"]
    readonly_fields = ["net_salary", "created_at", "updated_at"]
    date_hierarchy = "payment_date"