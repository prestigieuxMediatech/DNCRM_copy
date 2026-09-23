from django.contrib import admin

from .models import PunchSession


@admin.register(PunchSession)
class PunchSessionAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "date",
        "punch_in_at",
        "punch_out_at",
        "total_hours",
        "status",
    )
    list_filter = ("status", "date")
    search_fields = ("employee__first_name", "employee__last_name")
