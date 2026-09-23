from django.contrib import admin

from .models import Leave, Report


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "reviewed_by",
    )
    list_filter = ("leave_type", "status", "start_date")
    search_fields = ("employee__first_name", "employee__last_name", "reason")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("employee", "subject", "report_date", "submitted_at")
    list_filter = ("report_date",)
    search_fields = ("employee__first_name", "employee__last_name", "subject")
