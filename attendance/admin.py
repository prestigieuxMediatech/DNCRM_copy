from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "date",
        "day",
        "status",
        "working_hours",
        "remarks",
    )
    list_filter = ("status", "day", "date")
    search_fields = ("employee__first_name", "employee__last_name", "remarks")
