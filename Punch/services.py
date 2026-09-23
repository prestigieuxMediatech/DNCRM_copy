from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from attendance.services import create_attendance_from_punch, duration_to_hours

from .models import PunchSession


@transaction.atomic
def punch_in(employee, at_time=None):
    at_time = at_time or timezone.now()
    active_session = PunchSession.objects.filter(
        employee=employee,
        status="active",
    ).first()
    if active_session:
        return active_session
    
    today_session_exists = PunchSession.objects.filter( employee=employee, date=timezone.localdate(at_time), ).exists() 
    if today_session_exists:
        raise ValidationError( "Only one punch session is allowed per day." )


    return PunchSession.objects.create(
        employee=employee,
        date=timezone.localdate(at_time),
        punch_in_at=at_time,
        status="active",
    )


@transaction.atomic
def punch_out(employee, at_time=None):
    at_time = at_time or timezone.now()
    session = (
        PunchSession.objects.select_for_update()
        .filter(employee=employee, status="active")
        .order_by("-punch_in_at")
        .first()
    )
    if session is None:
        raise ValidationError("No active punch session found.")

    session.punch_out_at = at_time
    duration = session.punch_out_at - session.punch_in_at
    session.total_hours = duration_to_hours(duration)
    session.total_minutes = max(int(duration.total_seconds() // 60), 0)
    session.status = "completed"
    session.save(
        update_fields=[
            "punch_out_at",
            "total_hours",
            "total_minutes",
            "status",
            "updated_at",
        ]
    )
    create_attendance_from_punch(session)
    return session


# def auto_close_session(session, close_time=None):
#     close_time = close_time or timezone.now()
#     if session.status != "active":
#         return session

#     session.punch_out_at = close_time
#     duration = session.punch_out_at - session.punch_in_at
#     session.total_hours = duration_to_hours(duration)
#     session.total_minutes = max(int(duration.total_seconds() // 60), 0)
#     session.status = "auto_closed"
#     session.save(
#         update_fields=[
#             "punch_out_at",
#             "total_hours",
#             "total_minutes",
#             "status",
#             "updated_at",
#         ]
#     )
#     create_attendance_from_punch(session)
#     return session



@transaction.atomic
def auto_close_session(session, close_time=None):
    close_time = close_time or timezone.now()
    
    try:
        session = PunchSession.objects.select_for_update().get(
            pk=session.pk, 
            status="active"
        )
    except PunchSession.DoesNotExist:
        return session
    
    if close_time < session.punch_in_at:
        close_time = session.punch_in_at

    session.punch_out_at = close_time
    duration = session.punch_out_at - session.punch_in_at
    session.total_hours = duration_to_hours(duration)
    session.total_minutes = max(int(duration.total_seconds() // 60), 0)
    session.status = "auto_closed"
    session.save(
        update_fields=[
            "punch_out_at",
            "total_hours",
            "total_minutes",
            "status",
            "updated_at",
        ]
    )
    create_attendance_from_punch(session)
    return session