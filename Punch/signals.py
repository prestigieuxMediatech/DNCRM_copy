# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from attendance.services import create_attendance_from_punch

# from .models import PunchSession


# @receiver(post_save, sender=PunchSession)
# def create_attendance_when_session_closes(sender, instance, **kwargs):
#     if instance.status in {"completed", "auto_closed"} and instance.punch_out_at:
#         create_attendance_from_punch(instance)
