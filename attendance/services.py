from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from employees.models import Employee

from .models import Attendance
from django.core.cache import cache


PRESENT_HOURS = Decimal("6.00")
HALF_DAY_HOURS = Decimal("3.00")



def daterange(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)


def quantize_hours(hours):
    return Decimal(str(hours)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def duration_to_hours(duration):
    total_seconds = max(duration.total_seconds(), 0)
    return quantize_hours(total_seconds / 3600)


def status_for_working_hours(hours):
    hours = quantize_hours(hours)
    if hours >= PRESENT_HOURS:
        return "present"
    if hours >= HALF_DAY_HOURS:
        return "half_day"
    return "absent"



@transaction.atomic
def create_attendance_from_punch(session):
    if not session.punch_out_at:
        return None

    work_date = session.date or session.punch_in_at.date()
    hours = session.total_hours or duration_to_hours(
        session.punch_out_at - session.punch_in_at
    )
    status = status_for_working_hours(hours)

    attendance, _ = Attendance.objects.update_or_create(
        employee=session.employee,
        date=work_date,
        defaults={
            "day": work_date.strftime("%A"),
            "working_hours": hours,
            "status": status,
            "remarks": "Auto generated from punch session.",
        },
    )

    type(session).objects.filter(pk=session.pk).update(attendance=attendance)
    session.attendance = attendance
    return attendance


def create_or_update_attendance(session):
    return create_attendance_from_punch(session)


@transaction.atomic
def approve_leave_attendance(leave):
    records = []
    for leave_date in daterange(leave.start_date, leave.end_date):
        attendance, _ = Attendance.objects.update_or_create(
            employee=leave.employee,
            date=leave_date,
            defaults={
                "day": leave_date.strftime("%A"),
                "status": "leave",
                "working_hours": Decimal("0.00"),
                "leave_request": leave,
                "remarks": f"Approved {leave.get_leave_type_display()}",
            },
        )
        records.append(attendance)
    return records


def has_approved_leave(employee, date):
    return employee.leaves.filter(
        status="approved",
        start_date__lte=date,
        end_date__gte=date,
    ).exists()






# attendance/services.py

# @transaction.atomic
# def mark_absent_employees(target_date=None):
#     from Punch.models import PunchSession

#     target_date = target_date or timezone.localdate()

#     # ═══════════════════════════════════════════════════════════════
#     # 🟢 CACHE LOCK: Aaj ke liye already chal chuka hai toh wapas mat chalao
#     # ═══════════════════════════════════════════════════════════════
#     cache_key = f"absent_marked_{target_date.strftime('%Y_%m_%d')}"
#     if cache.get(cache_key):
#         print("✅ CACHE HIT: Already marked today, skipping DB")
#         return []  # Already done today, kuch mat karo



    
#     # 1. Saturday (5) & Sunday (6) ko Auto-Absent run mat hone do
#     if target_date.weekday() in [5, 6]:
#         return []

#     # 2. Sirf un Active Employees ko lo jo target_date tak join ho chuke hain
#     employees = Employee.objects.filter(
#         employment_status="ACTIVE",
#         joining_date__lte=target_date
#     ).only("id")

#     existing_attendance = set(
#         Attendance.objects.filter(date=target_date).values_list("employee_id", flat=True)
#     )
#     punched_employee_ids = set(
#         PunchSession.objects.filter(date=target_date).values_list("employee_id", flat=True)
#     )
#     approved_leave_ids = set(
#         Employee.objects.filter(
#             employment_status="ACTIVE",
#             leaves__status="approved",
#             leaves__start_date__lte=target_date,
#             leaves__end_date__gte=target_date,
#         ).values_list("id", flat=True)
#     )

#     absent_records = []
#     for employee in employees:
#         if employee.id in existing_attendance:
#             continue
#         if employee.id in punched_employee_ids:
#             continue
#         if employee.id in approved_leave_ids:
#             continue

     


#         attendance, created = Attendance.objects.get_or_create(
#             employee=employee,
#             date=target_date,
#             defaults={
#                 'day': target_date.strftime("%A"),
#                 'status': 'absent',
#                 'working_hours': Decimal("0.00"),
#                 'remarks': 'Auto marked absent after 6:00 PM office closing.',
#             }
#         )
#         if created:
#             absent_records.append(attendance)


#     cache.set(cache_key, True, timeout=60*60*18)

#     return absent_records





   # Database mein Save Hoga Automatically!
        # attendance = Attendance.objects.create(
        #     employee=employee,
        #     date=target_date,
        #     day=target_date.strftime("%A"),
        #     status="absent",
        #     working_hours=Decimal("0.00"),
        #     remarks="Auto marked absent after 6:00 PM office closing.",
        # )
        # absent_records.append(attendance)















# attendance/services.py

from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from employees.models import Employee
from .models import Attendance


# @transaction.atomic
# def mark_absent_employees(target_date=None):
#     from Punch.models import PunchSession

#     target_date = target_date or timezone.localdate()

#     # 1. Saturday (5) & Sunday (6) ko skip karein
#     if target_date.weekday() in [5, 6]:
#         return []

#     # 2. CACHE LOCK CHECK
#     cache_key = f"absent_marked_{target_date.strftime('%Y_%m_%d')}"
#     if cache.get(cache_key):
#         return []

#     # 3. Active Employees jo joining_date ke hisab se aaj hain
#     employees = Employee.objects.filter(
#         employment_status="ACTIVE",
#         joining_date__lte=target_date
#     )

#     existing_attendance = set(
#         Attendance.objects.filter(date=target_date).values_list("employee_id", flat=True)
#     )
#     punched_employee_ids = set(
#         PunchSession.objects.filter(date=target_date).values_list("employee_id", flat=True)
#     )
#     approved_leave_ids = set(
#         Employee.objects.filter(
#             employment_status="ACTIVE",
#             leaves__status="approved",
#             leaves__start_date__lte=target_date,
#             leaves__end_date__gte=target_date,
#         ).values_list("id", flat=True)
#     )

#     absent_records = []
#     for employee in employees:
#         if employee.id in existing_attendance:
#             continue
#         if employee.id in punched_employee_ids:
#             continue
#         if employee.id in approved_leave_ids:
#             continue

#         # Strictly absent insert karein bulk/single
#         attendance = Attendance.objects.create(
#             employee=employee,
#             date=target_date,
#             day=target_date.strftime("%A"),
#             status="absent",
#             working_hours=Decimal("0.00"),
#             remarks="Auto marked absent after 6:00 PM office closing.",
#         )
#         absent_records.append(attendance)

#     # SUCCESS: Sirf tabhi Cache lock karein jab process complete ho gaya ho
#     cache.set(cache_key, True, timeout=60 * 60 * 18)

#     return absent_records






































@transaction.atomic
def mark_absent_employees(target_date=None):
    from Punch.models import PunchSession
    from report.models import Leave  # Leave model import

    target_date = target_date or timezone.localdate()

    # Weekend Skip (Sat=5, Sun=6)
    if target_date.weekday() in [5, 6]:
        return []

    cache_key = f"absent_marked_{target_date.strftime('%Y_%m_%d')}"
    if cache.get(cache_key):
        return []

    # Active Employees who joined on or before target_date
    employees = Employee.objects.filter(
        employment_status="ACTIVE",
        joining_date__lte=target_date
    )

    existing_attendance = set(
        Attendance.objects.filter(date=target_date).values_list("employee_id", flat=True)
    )
    punched_employee_ids = set(
        PunchSession.objects.filter(date=target_date).values_list("employee_id", flat=True)
    )
    
    # Approved Leaves for target date
    approved_leave_ids = set(
        Leave.objects.filter(
            status="approved",
            start_date__lte=target_date,
            end_date__gte=target_date,
        ).values_list("employee_id", flat=True)
    )

    absent_records = []
    for employee in employees:
        if employee.id in existing_attendance:
            continue
        if employee.id in punched_employee_ids:
            continue
        if employee.id in approved_leave_ids:
            continue

        # DB Entry Create
        attendance = Attendance.objects.create(
            employee=employee,
            date=target_date,
            day=target_date.strftime("%A"),
            status="absent",
            working_hours=Decimal("0.00"),
            remarks="Auto marked absent after 6:00 PM office closing.",
        )
        absent_records.append(attendance)

    cache.set(cache_key, True, timeout=60 * 60 * 18)
    return absent_records

























# @transaction.atomic
# def mark_absent_employees(target_date=None):
#     from Punch.models import PunchSession

#     target_date = target_date or timezone.localdate()
#     employees = Employee.objects.filter(employment_status="ACTIVE").only("id")
#     existing_attendance = set(
#         Attendance.objects.filter(date=target_date).values_list("employee_id", flat=True)
#     )
#     punched_employee_ids = set(
#         PunchSession.objects.filter(date=target_date).values_list("employee_id", flat=True)
#     )
#     approved_leave_ids = set(
#         Employee.objects.filter(
#             employment_status="ACTIVE",
#             leaves__status="approved",
#             leaves__start_date__lte=target_date,
#             leaves__end_date__gte=target_date,
#         ).values_list("id", flat=True)
#     )

#     absent_records = []
#     for employee in employees:
#         if employee.id in existing_attendance:
#             continue
#         if employee.id in punched_employee_ids:
#             continue
#         if employee.id in approved_leave_ids:
#             continue

#         attendance = Attendance.objects.create(
#             employee=employee,
#             date=target_date,
#             day=target_date.strftime("%A"),
#             status="absent",
#             working_hours=Decimal("0.00"),
#             remarks="Auto marked absent by nightly attendance job.",
#         )
#         absent_records.append(attendance)

#     return absent_records
