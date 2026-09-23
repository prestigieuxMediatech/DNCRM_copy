# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from attendance.services import approve_leave_attendance

# from .models import Leave


# @receiver(post_save, sender=Leave)
# def create_attendance_for_approved_leave(sender, instance, **kwargs):
#     if instance.status == "approved":
#         approve_leave_attendance(instance)
