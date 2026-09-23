from django.db import transaction
from django.utils import timezone

from attendance.services import approve_leave_attendance


@transaction.atomic
def approve_leave(leave, reviewed_by):
    leave.status = "approved"
    leave.reviewed_by = reviewed_by
    leave.reviewed_at = timezone.now()
    leave.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
    approve_leave_attendance(leave)
    return leave


@transaction.atomic
def reject_leave(leave, reviewed_by):
    leave.status = "rejected"
    leave.reviewed_by = reviewed_by
    leave.reviewed_at = timezone.now()
    leave.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
    return leave
