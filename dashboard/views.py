from functools import wraps
import calendar
import json
from datetime import datetime, timedelta
import calendar
from calendar import monthrange

from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Count, Q, Prefetch, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.core.serializers.json import DjangoJSONEncoder
from projects.serializers import ProjectSerializer, ClientSerializer, EmployeeMiniSerializer
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.templatetags.static import static
from django.conf import settings
from datetime import date
from types import SimpleNamespace
from datetime import date, timedelta  # 🟢 timedelta ADD KAR
from django.db import IntegrityError, transaction  



from accounts.models import User
from attendance.models import Attendance
from employees.models import Department, Designation, Employee
from Punch.models import PunchSession
from Punch.serializers import PunchSessionSerializer
from Punch.services import punch_in, punch_out
from projects.models import Project, Client
from report.models import Leave, Report
from report.services import approve_leave, reject_leave
from projects.serializers import ClientDetailSerializer
from report.models import Leave
from payrolls.models import Payroll






import os
from django.conf import settings
from django.http import JsonResponse
from dashboard.utils import send_whatsapp




# import base64
# import requests
# from django.http import JsonResponse

# def send_whatsapp_api(request):
#     if request.method == "POST":
#         phone = request.POST.get('phone_number')
#         msg = request.POST.get('message', '')
        
#         file_base64 = None
#         filename = None
#         mimetype = None

#         if 'file_attachment' in request.FILES:
#             uploaded_file = request.FILES['file_attachment']
#             filename = uploaded_file.name
#             mimetype = uploaded_file.content_type or 'application/pdf'
            
#             # File read karke base64 string me convert karein
#             file_data = uploaded_file.read()
#             file_base64 = base64.b64encode(file_data).decode('utf-8')

#         # Microservice payload
#         payload = {
#             "phone_number": phone,
#             "message": msg,
#             "file_base64": file_base64,
#             "filename": filename,
#             "mimetype": mimetype
#         }

#                 # Django views.py
#         try:
#             response = requests.post("http://localhost:3000/send", json=payload, timeout=60)
#             return JsonResponse(response.json())
#         except requests.exceptions.Timeout:
#             return JsonResponse({'status': 'error', 'message': 'WhatsApp Service Ne Respond Nahi Kiya (Timeout)'})
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})






    #     try:
    #         response = requests.post("http://localhost:3000/send", json=payload, timeout=30)
    #         return JsonResponse(response.json())
    #     except Exception as e:
    #         return JsonResponse({'status': 'error', 'message': str(e)})

    # return JsonResponse({'status': 'error', 'message': 'Invalid Request'})













import base64
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required

WHATSAPP_SERVICE_URL = "http://localhost:3000/send"


# @login_required   # chahein to enable kar lena
@require_POST
def send_whatsapp_api(request):
    phone = request.POST.get('phone_number', '').strip()
    msg = request.POST.get('message', '')

    if not phone:
        return JsonResponse(
            {'status': 'error', 'message': 'Phone number required hai'},
            status=400
        )

    file_base64 = None
    filename = None
    mimetype = None

    uploaded_file = request.FILES.get('file_attachment')
    if uploaded_file:
        filename = uploaded_file.name
        mimetype = uploaded_file.content_type or 'application/pdf'
        file_base64 = base64.b64encode(uploaded_file.read()).decode('utf-8')

    payload = {
        "phone_number": phone,
        "message": msg,
        "file_base64": file_base64,
        "filename": filename,
        "mimetype": mimetype,
    }

    try:
        response = requests.post(WHATSAPP_SERVICE_URL, json=payload, timeout=120)
        try:
            data = response.json()
        except ValueError:
            data = {'status': 'error', 'message': 'WhatsApp service se invalid response aaya'}
        return JsonResponse(data, status=response.status_code)

    except requests.exceptions.Timeout:
        return JsonResponse(
            {'status': 'error', 'message': 'WhatsApp service ne respond nahi kiya (Timeout)'},
            status=504
        )
    except requests.exceptions.ConnectionError:
        return JsonResponse(
            {'status': 'error', 'message': 'WhatsApp service band hai. Node service (port 3000) start karo.'},
            status=503
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)




























































def role_required(*allowed_roles):
    """Allow authenticated users with one of the given application roles."""
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


@role_required("admin")
def admin_dashboard(request):
    today = timezone.localdate()
    employees = Employee.objects.select_related("department", "designation").order_by("-created_at")
    present_count = Attendance.objects.filter(
        date=today,
        status__in=["present", "half_day", "leave"],
    ).count()
    total_employees = employees.count()
    attendance_percentage = round((present_count / total_employees) * 100) if total_employees else 0
    today_punch_sessions = PunchSession.objects.filter(date=today).count()
    context = {
        "total_employees": total_employees,
        "total_departments": Department.objects.count(),
        "total_designations": Designation.objects.count(),
        "attendance_percentage": attendance_percentage,
        "employees": employees[:5],
        "pending_leaves": Leave.objects.select_related("employee", "employee__user")
        .filter(status="pending")
        .order_by("start_date")[:10],
        "today_punch_sessions": today_punch_sessions,
    }
    return render(request, "admin/dashboard.html", context)



# ── User API: List + Create ───────────────────────────────
@role_required("admin")
@require_http_methods(["GET", "POST"])
def user_api(request):

    if request.method == "GET":
        users = User.objects.all().order_by('-created_at')
        return JsonResponse({'users': [serialize_user(u) for u in users]})

    body             = json.loads(request.body)
    email            = body.get('email', '').strip().lower()
    role             = body.get('role', '')
    password         = body.get('password', '')
    confirm_password = body.get('confirm_password', '')
    is_active        = body.get('is_active', True)
    is_staff         = body.get('is_staff', False)

    if not email or not role or not password:
        return JsonResponse({'error': 'Email, role and password are required'}, status=400)
    if password != confirm_password:
        return JsonResponse({'error': 'Passwords do not match'}, status=400)
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email already exists'}, status=400)

    user = User.objects.create_user(
        email=email, password=password,
        role=role, is_active=is_active, is_staff=is_staff,
    )
    return JsonResponse({'message': 'User added successfully', 'user': serialize_user(user)}, status=201)


# ── User API: Edit + Delete ───────────────────────────────
@role_required("admin")
@require_http_methods(["PUT", "DELETE"])
def user_detail_api(request, user_id):

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    if request.method == "DELETE":
        if user.is_superuser:
            return JsonResponse({'error': 'Cannot delete superuser'}, status=403)
        user.delete()
        return JsonResponse({'message': 'User deleted'})

    body      = json.loads(request.body)
    email     = body.get('email', '').strip().lower()
    role      = body.get('role', '')
    password  = body.get('password', '')
    is_active = body.get('is_active', True)
    is_staff  = body.get('is_staff', False)

    if not email or not role:
        return JsonResponse({'error': 'Email and role are required'}, status=400)
    if User.objects.filter(email=email).exclude(id=user_id).exists():
        return JsonResponse({'error': 'Email already exists'}, status=400)

    user.email     = email
    user.role      = role
    user.is_active = is_active
    user.is_staff  = is_staff
    if password:
        user.set_password(password)
    user.save()

    return JsonResponse({'message': 'User updated successfully', 'user': serialize_user(user)})


# ── Serialize Helper ──────────────────────────────────────
def serialize_user(u):
    return {
        'id': u.id, 'email': u.email, 'role': u.role,
        'is_active': u.is_active, 'is_staff': u.is_staff,
        'is_superuser': u.is_superuser,
    }























































@role_required("employee")
def employee_dashboard(request):
    employee = get_object_or_404(Employee, user=request.user)
    today = timezone.localdate()
    assigned_projects = (
        Project.objects
        .filter(employees=employee)
        .select_related("client")
        .distinct()
    )
    active_session = PunchSession.objects.filter(
        employee=employee,
        status="active",
    ).first()
    today_session = PunchSession.objects.filter(
        employee=employee,
        date=today,
    ).order_by("-punch_in_at").first()
    today_attendance = Attendance.objects.filter(employee=employee, date=today).first()
    pending_projects = assigned_projects.filter(status="in_progress").order_by("-updated_at", "-created_at")
    approved_leaves = Leave.objects.filter(employee=employee, status="approved").count()
    leave_requests = Leave.objects.filter(employee=employee).count()

    if active_session:
        today_status = "Punched In"
    elif today_session and today_session.status in ["completed", "auto_closed"]:
        today_status = "Punched Out"
    elif today_attendance and today_attendance.status == "present":
        today_status = "Present"
    else:
        today_status = "Absent"

    context = {
        "employee": employee,
        "active_session": active_session,
        "today_attendance": today_attendance,
        "active_projects": assigned_projects.exclude(status__in=["completed", "cancelled"]).count(),
        "pending_projects": pending_projects[:5],
        "approved_leaves": approved_leaves,
        "leave_requests": leave_requests,
        "today_status": today_status,
        "today": today,
    }
    return render(request, "employee/dashboard.html", context)


# @role_required("employee")
# @require_POST
# def employee_punch_in(request):
#     employee = get_object_or_404(Employee, user=request.user)
#     session = punch_in(employee)
#     if session.status == "active":
#         messages.success(request, "Punch in started successfully.")
#     return redirect("dashboard:employee_dashboard")


# @role_required("employee")
# @require_POST
# def employee_punch_in(request): 
#     employee = get_object_or_404(Employee, user=request.user) 
#     try:
#         session = punch_in(employee)
#         if session.status == "active": 
#             messages.success(request, "Punch in started successfully.")
#     except ValidationError as e:
#         messages.error(request, e.messages[0]) 
#     return redirect("dashboard:employee_dashboard")


@role_required("employee")
@require_POST
def employee_punch_out(request):
    employee = get_object_or_404(Employee, user=request.user)
    try:
        punch_out(employee)
        messages.success(request, "Punch out completed. Attendance updated automatically.")
    except ValidationError as exc:
        messages.error(request, exc.message)
    return redirect("dashboard:employee_dashboard")


# @role_required("employee")
# def employee_reports(request):
#     employee = get_object_or_404(Employee, user=request.user)
#     today = timezone.localdate()
#     if request.method == "POST":
#         if "submit_report" in request.POST:
#             subject = request.POST.get("taskCompleted", "").strip()
#             work_summary = request.POST.get("workSummary", "").strip()
#             if not subject or not work_summary:
#                 messages.error(request, "Please fill report subject and work summary.")
#             else:
#                 report, created = Report.objects.update_or_create(
#                     employee=employee,
#                     report_date=today,
#                     defaults={
#                         "subject": subject,
#                         "work_summary": work_summary,
#                     },
#                 )

#                 # ✅ Handle optional image upload
#                 if "attachment" in request.FILES:
#                     report.attachment = request.FILES["attachment"]
#                     report.save()
#                 messages.success(request, "Daily work report submitted.")
#                 return redirect("dashboard:employee_reports")

#         leave_type_map = {
#             "Casual Leave": "casual_leave",
#             "Sick Leave": "sick_leave",
#             "Paid Leave": "paid_leave",
#             "Emergency Leave": "emergency_leave",
#             "Unpaid Leave": "unpaid_leave", 
#         }
#         leave_type = (
#             request.POST.get("leave_type")
#             or request.POST.get("leaveType")
#             or ""
#         )
#         leave_type = leave_type_map.get(leave_type, leave_type)
#         start_date = parse_date(
#             request.POST.get("start_date", "") or request.POST.get("startDate", "")
#         )
#         end_date = parse_date(
#             request.POST.get("end_date", "") or request.POST.get("endDate", "")
#         )
#         reason = request.POST.get("reason", "").strip()

#         valid_leave_types = {value for value, _ in Leave.LEAVE_TYPE_CHOICES}
#         if not leave_type or leave_type not in valid_leave_types or not start_date or not end_date or not reason:
#             messages.error(request, "Please fill all leave request fields.")
#         elif end_date < start_date:
#             messages.error(request, "End date cannot be before start date.")
#         else:
#             Leave.objects.create(
#                 employee=employee,
#                 leave_type=leave_type,
#                 start_date=start_date,
#                 end_date=end_date,
#                 reason=reason,
#             )
#             messages.success(request, "Leave request submitted for admin approval.")
#             return redirect("dashboard:employee_reports")

#     context = {
#         "employee": employee,
#         "leave_types": Leave.LEAVE_TYPE_CHOICES,
#         "leaves": Leave.objects.filter(employee=employee).order_by("-id"),
#         "reports_count": Report.objects.filter(
#             employee=employee,
#             report_date__year=today.year,
#             report_date__month=today.month,
#         ).count(),
#         "leave_count": Leave.objects.filter(employee=employee, status="pending").count(),
#     }
#     return render(request, "employee/reports.html", context)












# views.py file me:

@role_required("employee")
def employee_reports(request):
    employee = get_object_or_404(Employee, user=request.user)
    today = timezone.localdate()

    # 🟢 STEP 1: Jab user koi bhi form submit (POST) karega
    if request.method == "POST":

        # 🟢 STEP 2: YAHAN LIKHNA HAI NAYA WAY (IF / ELIF)
        
        # Scenario A: Jab "Daily Work Report" form submit hua ho
        if "submit_report" in request.POST:
            subject = request.POST.get("taskCompleted", "").strip()
            work_summary = request.POST.get("workSummary", "").strip()
            attachment = request.FILES.get("attachment")

            if not subject or not work_summary:
                messages.error(request, "Please fill report subject and work summary.")
            else:
                defaults_data = {
                    "subject": subject,
                    "work_summary": work_summary,
                }
                if attachment:
                    defaults_data["attachment"] = attachment

                Report.objects.update_or_create(
                    employee=employee,
                    report_date=today,
                    defaults=defaults_data,
                )
                messages.success(request, "Daily work report submitted successfully.")
            
            return redirect("dashboard:employee_reports")

        # Scenario B: Jab "Leave Request" form submit hua ho
        elif "submit_leave" in request.POST:
            leave_type_map = {
                "Casual Leave": "casual_leave",
                "Sick Leave": "sick_leave",
                "Paid Leave": "paid_leave",
                "Emergency Leave": "emergency_leave",
                "Unpaid Leave": "unpaid_leave", 
            }
            raw_leave_type = request.POST.get("leaveType") or request.POST.get("leave_type") or ""
            leave_type = leave_type_map.get(raw_leave_type, raw_leave_type)
            
            start_date = parse_date(request.POST.get("startDate", "") or request.POST.get("start_date", ""))
            end_date = parse_date(request.POST.get("endDate", "") or request.POST.get("end_date", ""))
            reason = request.POST.get("reason", "").strip()

            valid_leave_types = {value for value, _ in Leave.LEAVE_TYPE_CHOICES}

            if not leave_type or leave_type not in valid_leave_types or not start_date or not end_date or not reason:
                messages.error(request, "Please fill all leave request fields.")
            elif end_date < start_date:
                messages.error(request, "End date cannot be before start date.")
            else:
                Leave.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    reason=reason,
                )
                messages.success(request, "Leave request submitted for admin approval.")
            
            return redirect("dashboard:employee_reports")

    # 🟢 STEP 3: Simple GET Request (Page Load hone par)
    context = {
        "employee": employee,
        "leave_types": Leave.LEAVE_TYPE_CHOICES,
        "leaves": Leave.objects.filter(employee=employee).order_by("-id"),
        "reports_count": Report.objects.filter(
            employee=employee,
            report_date__year=today.year,
            report_date__month=today.month,
        ).count(),
        "leave_count": Leave.objects.filter(employee=employee, status="pending").count(),
    }
    return render(request, "employee/reports.html", context)


























from attendance.services import mark_absent_employees

# @role_required("employee")
# def employee_attendance(request):

#     # if timezone.localtime().hour >= 18:
#     #    mark_absent_employees(target_date=timezone.localdate())

#     employee = get_object_or_404(Employee, user=request.user)
#     today = timezone.localdate()
#     month_param = request.GET.get("month")
#     year_param = request.GET.get("year")
#     show_current_month = request.GET.get("reset") == "current"

#     if show_current_month:
#         selected_month = today.month
#         selected_year = today.year
#     else:
#         try:
#             selected_month = int(month_param) if month_param else today.month
#         except (TypeError, ValueError):
#             selected_month = today.month

#         try:
#             selected_year = int(year_param) if year_param else today.year
#         except (TypeError, ValueError):
#             selected_year = today.year

#         if selected_month < 1 or selected_month > 12:
#             selected_month = today.month

#     if selected_month == today.month and selected_year == today.year:
#         if timezone.localtime().hour >= 18:
#             mark_absent_employees(target_date=today)

#     attendance_years = [
#         attendance_year.year
#         for attendance_year in Attendance.objects.filter(employee=employee).dates(
#             "date",
#             "year",
#             order="DESC",
#         )
#     ]
#     year_options = sorted(
#         set(attendance_years + [today.year, today.year - 1, today.year - 2, selected_year]),
#         reverse=True,
#     )
#     selected_label = f"{calendar.month_name[selected_month]} {selected_year}"

#     # ═══════════════════════════════════════════════════════════════
#     # 🟢 SIRF YEH PART BADLA HAI — Poora mahina dikhane ke liye
#     # ═══════════════════════════════════════════════════════════════

#     # 1. Asli DB records (summary counts ke liye alag se rakho)
#     attendance_records = Attendance.objects.filter(
#         employee=employee,
#         date__year=selected_year,
#         date__month=selected_month,
#     )

#     # 2. Fast lookup: date -> record
#     db_map = {a.date: a for a in attendance_records}

#     # 3. 1 se last date tak loop chalao
#     _, last_day = calendar.monthrange(selected_year, selected_month)
#     full_attendances = []

#     for day_num in range(1, last_day + 1):
#         current_date = date(selected_year, selected_month, day_num)

#         if current_date in db_map:
#             # Asli database record hai
#             full_attendances.append(db_map[current_date])

#         elif current_date.weekday() in (5, 6):   # Saturday=5, Sunday=6
#             # Weekend ke liye fake row
#             full_attendances.append(SimpleNamespace(
#                 date=current_date,
#                 day=current_date.strftime("%A"),
#                 status="weekend",
#                 remarks="Week Off",
#             ))
#         else:
#             # Aise din jisme abhi koi record nahi (future ya unmarked)
#             full_attendances.append(SimpleNamespace(
#                 date=current_date,
#                 day=current_date.strftime("%A"),
#                 status="not_marked",
#                 remarks="-",
#             ))

#     # 4. Descending order (sabse recent pehle)
#     full_attendances.sort(key=lambda x: x.date, reverse=True)

#     # ═══════════════════════════════════════════════════════════════

#     context = {
#         "employee": employee,
#         "attendances": full_attendances,          # ← Ab poora mahina hai
#         "current_month": selected_label,
#         "selected_month": selected_month,
#         "selected_year": selected_year,
#         "current_month_number": today.month,
#         "current_year": today.year,
#         "month_options": [(month, calendar.month_name[month]) for month in range(1, 13)],
#         "year_options": year_options,
#         # Summary cards sirf asli DB records se count honge — weekend affect nahi karega
#         "present_days": attendance_records.filter(status="present").count(),
#         "absent_days": attendance_records.filter(status="absent").count(),
#         "leave_days": attendance_records.filter(status="leave").count(),
#         "half_days": attendance_records.filter(status="half_day").count(),
#     }
#     return render(request, "employee/attendance.html", context)









from datetime import date, timedelta          # 🟢 timedelta ADD KIYA
from types import SimpleNamespace
import calendar
from django.utils import timezone
from django.shortcuts import get_object_or_404

from report.models import Leave                # 🟢 Leave model IMPORT KIYA

# ... baaki imports same ...

# @role_required("employee")
# def employee_attendance(request):

#     # if timezone.localtime().hour >= 18:
#     #    mark_absent_employees(target_date=timezone.localdate())

#     employee = get_object_or_404(Employee, user=request.user)
#     today = timezone.localdate()
#     month_param = request.GET.get("month")
#     year_param = request.GET.get("year")
#     show_current_month = request.GET.get("reset") == "current"

#     if show_current_month:
#         selected_month = today.month
#         selected_year = today.year
#     else:
#         try:
#             selected_month = int(month_param) if month_param else today.month
#         except (TypeError, ValueError):
#             selected_month = today.month

#         try:
#             selected_year = int(year_param) if year_param else today.year
#         except (TypeError, ValueError):
#             selected_year = today.year

#         if selected_month < 1 or selected_month > 12:
#             selected_month = today.month

#     if selected_month == today.month and selected_year == today.year:
#         if timezone.localtime().hour >= 18:
#             mark_absent_employees(target_date=today)

#     attendance_years = [
#         attendance_year.year
#         for attendance_year in Attendance.objects.filter(employee=employee).dates(
#             "date",
#             "year",
#             order="DESC",
#         )
#     ]
#     year_options = sorted(
#         set(attendance_years + [today.year, today.year - 1, today.year - 2, selected_year]),
#         reverse=True,
#     )
#     selected_label = f"{calendar.month_name[selected_month]} {selected_year}"

#     # ═══════════════════════════════════════════════════════════════
#     # 1. Asli DB records (summary counts ke liye alag se rakho)
#     # ═══════════════════════════════════════════════════════════════
#     attendance_records = Attendance.objects.filter(
#         employee=employee,
#         date__year=selected_year,
#         date__month=selected_month,
#     )

#     # ═══════════════════════════════════════════════════════════════
#     # 🟢 2. APPROVED LEAVES FETCH KARO — YEH NAYA BLOCK HAI
#     # ═══════════════════════════════════════════════════════════════
#     _, last_day = calendar.monthrange(selected_year, selected_month)

#     approved_leaves = Leave.objects.filter(
#         employee=employee,
#         status="approved",
#         start_date__lte=date(selected_year, selected_month, last_day),
#         end_date__gte=date(selected_year, selected_month, 1),
#     )

#     approved_leave_dates = set()
#     for leave in approved_leaves:
#         current = max(leave.start_date, date(selected_year, selected_month, 1))
#         end = min(leave.end_date, date(selected_year, selected_month, last_day))
#         while current <= end:
#             approved_leave_dates.add(current)
#             current += timedelta(days=1)
#     # ═══════════════════════════════════════════════════════════════

#     # 3. Fast lookup: date -> record
#     db_map = {a.date: a for a in attendance_records}

#     # 4. 1 se last date tak loop chalao
#     full_attendances = []

#     for day_num in range(1, last_day + 1):
#         current_date = date(selected_year, selected_month, day_num)

#         if current_date in db_map:
#             # Asli database record hai
#             record = db_map[current_date]

#             # 🟢 AGAR admin ne leave approve ki hai, toh status "leave" hona chahiye
#             if current_date in approved_leave_dates:
#                 record.status = "leave"
#                 if not record.remarks or record.remarks == "-":
#                     record.remarks = "Approved Leave"

#             full_attendances.append(record)

#         # 🟢 APPROVED LEAVE HAI PAR ATTENDANCE RECORD NAHI BANA — YEH NAYA ELIF HAI
#         elif current_date in approved_leave_dates:
#             full_attendances.append(SimpleNamespace(
#                 date=current_date,
#                 day=current_date.strftime("%A"),
#                 status="leave",
#                 remarks="Approved Leave",
#             ))

#         elif current_date.weekday() in (5, 6):   # Saturday=5, Sunday=6
#             # Weekend ke liye fake row
#             full_attendances.append(SimpleNamespace(
#                 date=current_date,
#                 day=current_date.strftime("%A"),
#                 status="weekend",
#                 remarks="Week Off",
#             ))
#         else:
#             # Aise din jisme abhi koi record nahi (future ya unmarked)
#             full_attendances.append(SimpleNamespace(
#                 date=current_date,
#                 day=current_date.strftime("%A"),
#                 status="not_marked",
#                 remarks="-",
#             ))

#     # 5. Descending order (sabse recent pehle)
#     full_attendances.sort(key=lambda x: x.date, reverse=True)

#     # ═══════════════════════════════════════════════════════════════
#     # CONTEXT
#     # ═══════════════════════════════════════════════════════════════
#     context = {
#         "employee": employee,
#         "attendances": full_attendances,          # ← Ab poora mahina hai
#         "current_month": selected_label,
#         "selected_month": selected_month,
#         "selected_year": selected_year,
#         "current_month_number": today.month,
#         "current_year": today.year,
#         "month_options": [(month, calendar.month_name[month]) for month in range(1, 13)],
#         "year_options": year_options,
#         # Summary cards sirf asli DB records se count honge
#         "present_days": attendance_records.filter(status="present").count(),
#         "absent_days": attendance_records.filter(status="absent").count(),
#         "leave_days": attendance_records.filter(status="leave").count(),
#         "half_days": attendance_records.filter(status="half_day").count(),
#     }
#     return render(request, "employee/attendance.html", context)


































@role_required("employee")
def employee_attendance(request):

    employee = get_object_or_404(Employee, user=request.user)
    today = timezone.localdate()
    now = timezone.localtime()
    
    month_param = request.GET.get("month")
    year_param = request.GET.get("year")
    show_current_month = request.GET.get("reset") == "current"

    if show_current_month:
        selected_month = today.month
        selected_year = today.year
    else:
        try:
            selected_month = int(month_param) if month_param else today.month
        except (TypeError, ValueError):
            selected_month = today.month

        try:
            selected_year = int(year_param) if year_param else today.year
        except (TypeError, ValueError):
            selected_year = today.year

        if selected_month < 1 or selected_month > 12:
            selected_month = today.month

    # Shaam 6 baje ke baad DB level par bhi absent mark trigger kar rahe hain
    if selected_month == today.month and selected_year == today.year:
        if now.hour >= 18:
            mark_absent_employees(target_date=today)

    attendance_years = [
        attendance_year.year
        for attendance_year in Attendance.objects.filter(employee=employee).dates(
            "date",
            "year",
            order="DESC",
        )
    ]
    year_options = sorted(
        set(attendance_years + [today.year, today.year - 1, today.year - 2, selected_year]),
        reverse=True,
    )
    selected_label = f"{calendar.month_name[selected_month]} {selected_year}"

    # 1. Asli DB records
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__year=selected_year,
        date__month=selected_month,
    )

    # 2. Approved Leaves
    _, last_day = calendar.monthrange(selected_year, selected_month)

    approved_leaves = Leave.objects.filter(
        employee=employee,
        status="approved",
        start_date__lte=date(selected_year, selected_month, last_day),
        end_date__gte=date(selected_year, selected_month, 1),
    )

    approved_leave_dates = set()
    for leave in approved_leaves:
        current = max(leave.start_date, date(selected_year, selected_month, 1))
        end = min(leave.end_date, date(selected_year, selected_month, last_day))
        while current <= end:
            approved_leave_dates.add(current)
            current += timedelta(days=1)

    # 3. Fast lookup: date -> record
    db_map = {a.date: a for a in attendance_records}

    # 4. 1 se last date tak loop chalao
    full_attendances = []

    for day_num in range(1, last_day + 1):
        current_date = date(selected_year, selected_month, day_num)

        # DB me pehle se record exist karta hai
        if current_date in db_map:
            record = db_map[current_date]

            if current_date in approved_leave_dates:
                record.status = "leave"
                if not record.remarks or record.remarks == "-":
                    record.remarks = "Approved Leave"

            full_attendances.append(record)

        # Approved leave par hai
        elif current_date in approved_leave_dates:
            full_attendances.append(SimpleNamespace(
                date=current_date,
                day=current_date.strftime("%A"),
                status="leave",
                remarks="Approved Leave",
            ))

        # Weekend (Sat / Sun)
        elif current_date.weekday() in (5, 6):
            full_attendances.append(SimpleNamespace(
                date=current_date,
                day=current_date.strftime("%A"),
                status="weekend",
                remarks="Week Off",
            ))

        # BEETE HUE DIN: Agar pichle dino me koi record/punch nahi hai -> ABSENT
        elif current_date < today:
            full_attendances.append(SimpleNamespace(
                date=current_date,
                day=current_date.strftime("%A"),
                status="absent",
                remarks="Absent",
            ))

        # AAJ KA DIN: Shaam 6 Baje (18:00) ke baad tak agar punch nahi hua -> ABSENT
        elif current_date == today:
            if now.hour >= 18:
                full_attendances.append(SimpleNamespace(
                    date=current_date,
                    day=current_date.strftime("%A"),
                    status="absent",
                    remarks="Absent",
                ))
            else:
                # Shaam 6 baje se pehle tak Pending / Not Marked dikhega
                full_attendances.append(SimpleNamespace(
                    date=current_date,
                    day=current_date.strftime("%A"),
                    status="not_marked",
                    remarks="-",
                ))

        # AANE WALE DIN (Future Dates)
        else:
            full_attendances.append(SimpleNamespace(
                date=current_date,
                day=current_date.strftime("%A"),
                status="not_marked",
                remarks="-",
            ))

    # 5. Descending order (Recent date pehle)
    full_attendances.sort(key=lambda x: x.date, reverse=True)

    # CONTEXT
    context = {
        "employee": employee,
        "attendances": full_attendances,
        "current_month": selected_label,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "current_month_number": today.month,
        "current_year": today.year,
        "month_options": [(month, calendar.month_name[month]) for month in range(1, 13)],
        "year_options": year_options,
        "present_days": attendance_records.filter(status="present").count(),
        "absent_days": attendance_records.filter(status="absent").count(),
        "leave_days": attendance_records.filter(status="leave").count(),
        "half_days": attendance_records.filter(status="half_day").count(),
    }
    return render(request, "employee/attendance.html", context)













































































def format_seconds(total_seconds):
    total_seconds = max(int(total_seconds), 0)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}h {minutes:02d}m"





















# @role_required("employee")
# def employee_attendance(request):

#     # if timezone.localtime().hour >= 18:
#     #    mark_absent_employees(target_date=timezone.localdate())




#     employee = get_object_or_404(Employee, user=request.user)
#     today = timezone.localdate()
#     month_param = request.GET.get("month")
#     year_param = request.GET.get("year")
#     show_current_month = request.GET.get("reset") == "current"

#     if show_current_month:
#         selected_month = today.month
#         selected_year = today.year
#     else:
#         try:
#             selected_month = int(month_param) if month_param else today.month
#         except (TypeError, ValueError):
#             selected_month = today.month

#         try:
#             selected_year = int(year_param) if year_param else today.year
#         except (TypeError, ValueError):
#             selected_year = today.year

#         if selected_month < 1 or selected_month > 12:
#             selected_month = today.month

#     if selected_month == today.month and selected_year == today.year:
#         if timezone.localtime().hour >= 18:
#             mark_absent_employees(target_date=today)

#     attendance_years = [
#         attendance_year.year
#         for attendance_year in Attendance.objects.filter(employee=employee).dates(
#             "date",
#             "year",
#             order="DESC",
#         )
#     ]
#     year_options = sorted(
#         set(attendance_years + [today.year, today.year - 1, today.year - 2, selected_year]),
#         reverse=True,
#     )
#     selected_label = f"{calendar.month_name[selected_month]} {selected_year}"



#     attendances = Attendance.objects.filter(
#         employee=employee,
#         date__year=selected_year,
#         date__month=selected_month,
#     ).order_by("-date")
#     context = {
#         "employee": employee,
#         "attendances": attendances,
#         "current_month": selected_label,
#         "selected_month": selected_month,
#         "selected_year": selected_year,
#         "current_month_number": today.month,
#         "current_year": today.year,
#         "month_options": [(month, calendar.month_name[month]) for month in range(1, 13)],
#         "year_options": year_options,
#         "present_days": attendances.filter(status="present").count(),
#         "absent_days": attendances.filter(status="absent").count(),
#         "leave_days": attendances.filter(status="leave").count(),
#         "half_days": attendances.filter(status="half_day").count(),
#     }
#     return render(request, "employee/attendance.html", context)


# def format_seconds(total_seconds):
#     total_seconds = max(int(total_seconds), 0)
#     hours = total_seconds // 3600
#     minutes = (total_seconds % 3600) // 60
#     return f"{hours}h {minutes:02d}m"


from datetime import time  # ← NAYA IMPORT
from Punch.services import auto_close_session  # ← NAYA IMPORT (agar pehle se nahi hai)

@role_required("employee")
def employee_punchin(request):
    employee = get_object_or_404(Employee, user=request.user)
    today = timezone.localdate()      # ← ADD
    now = timezone.localtime() 

    # # ===== LAZY AUTO-CLOSE START =====
    # # 1. Purane din (kal, parso) ka active session close karo
    # stale_sessions = PunchSession.objects.filter(
    #     employee=employee,
    #     status="active",
    #     date__lt=today,
    # )
    # for session in stale_sessions:
    #     six_pm = timezone.make_aware(
    #         timezone.datetime.combine(
    #             session.date, 
    #             timezone.datetime.min.time().replace(hour=18)
    #         )
    #     )
    #     auto_close_session(session, six_pm)


     
    # # 2. Aaj ka session agar 6:10 PM cross ho gaya
    # if now.time() >= time(18, 10):
    #     today_stale = PunchSession.objects.filter(
    #         employee=employee,
    #         status="active",
    #         date=today,
    #         punch_in_at__hour__lt=18,
    #     ).first()
    #     if today_stale:
    #         close_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
    #         auto_close_session(today_stale, close_time)
    # # ===== LAZY AUTO-CLOSE END =====





    
    if request.method == "POST":
        if "punch_out" in request.POST:
            try:
                punch_out(employee)
                messages.success(request, "Punch out completed. Attendance updated automatically.")
            except ValidationError as exc:
                messages.error(request, exc.message)
        else:
            try:
                punch_in(employee)
                messages.success(request, "Punch in started successfully.")
            except ValidationError as e:
                      messages.error(request, e.messages[0])

            return redirect("dashboard:employee_punchin")

    active_session = PunchSession.objects.filter(
        employee=employee,
        status="active",
        date=today,
    ).first()
    elapsed_seconds = 0
    if active_session:
        elapsed_seconds = (timezone.now() - active_session.punch_in_at).total_seconds()

    office_end = timezone.localtime().replace(hour=18, minute=0, second=0, microsecond=0)
    remaining_seconds = (office_end - timezone.localtime()).total_seconds()
    context = {
        "employee": employee,
        "active_session": active_session,
        "working_hours": format_seconds(elapsed_seconds),
        "remaining_hours": format_seconds(remaining_seconds),
    }
    return render(request, "employee/punchin.html", context)








@role_required("admin")
@require_POST
def admin_approve_leave(request, leave_id):
    leave = get_object_or_404(Leave, pk=leave_id)
    approve_leave(leave, request.user)
    messages.success(request, "Leave approved and attendance updated automatically.")
    return redirect("dashboard:admin_dashboard")


@role_required("admin")
@require_POST
def admin_reject_leave(request, leave_id):
    leave = get_object_or_404(Leave, pk=leave_id)
    reject_leave(leave, request.user)
    messages.success(request, "Leave rejected.")
    return redirect("dashboard:admin_dashboard")


@role_required("employee")
def employee_profile(request):
    employee = get_object_or_404(Employee, user=request.user)
    return render(request, "employee/profile.html", {"employee": employee})


@role_required("employee")
def employee_projects(request):
    employee = get_object_or_404(Employee, user=request.user)
    assigned_projects = (
        Project.objects
        .filter(employees=employee)
        .select_related("client")
        .distinct()
        .order_by("-created_at")
    )

    active_view = request.GET.get("view", "all")
    view_titles = {
        "all": "All Projects",
        "in_progress": "In Progress Projects", 
        "completed": "Completed Projects",
        "upcoming": "Upcoming Projects",
    }
    if active_view not in view_titles:
        active_view = "all"

    filtered_projects = assigned_projects
    if active_view == "in_progress":
        filtered_projects = assigned_projects.filter(status="in_progress")
    elif active_view == "completed":
        filtered_projects = assigned_projects.filter(status="completed")
    elif active_view == "upcoming":
        filtered_projects = assigned_projects.filter(status="on_hold")

    context = {
        "employee": employee,
        "projects": filtered_projects,
        "active_view": active_view,
        "projects_title": view_titles[active_view],
        "total_projects": assigned_projects.count(),
        "in_progress_projects": assigned_projects.filter(status="in_progress").count(),
        "completed_projects": assigned_projects.filter(status="completed").count(),
        "upcoming_projects": assigned_projects.filter(status="on_hold").count(),
    }
    return render(request, "employee/projects.html", context)



# *****************                 admin dashboard views                 ******************


@role_required("admin")
@ensure_csrf_cookie
def user_list(request):
    users = User.objects.all().order_by("-created_at")
    return render(request, "admin/user.html", {"users": users})


# ─── EMPLOYEE LIST ───
@login_required
def employee_list(request):
    employees = Employee.objects.select_related('user', 'department', 'designation').all().order_by('id')
    pending_employee_users = User.objects.filter(
        role="employee",
        employee_profile__isnull=True,
    ).order_by("id")
    
    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(employee_code__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
        pending_employee_users = pending_employee_users.filter(email__icontains=search_query)
    
    # Department filter
    dept_filter = request.GET.get('department', '')
    if dept_filter:
        employees = employees.filter(department_id=dept_filter)
        pending_employee_users = pending_employee_users.none()
    
    # Departments for dropdown filter
    departments = Department.objects.all().order_by('name')
    
    context = {
        'employees': employees,
        'pending_employee_users': pending_employee_users,
        'departments': departments,
        'search_query': search_query,
        'dept_filter': dept_filter,
    }
    return render(request, 'admin/employee.html', context)



# ─── ADD EMPLOYEE ───
@login_required
def add_employee(request):
    if request.method == 'POST':
        # Direct POST data se nikaal rahe hain
        user_id = request.POST.get('user')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        dob = request.POST.get('dob') or None
        emergency_contact = request.POST.get('emergency_contact', '').strip()
        bio = request.POST.get('bio', '').strip()
        skills_raw = request.POST.get('skills', '')
        status = request.POST.get('status', 'ACTIVE').upper()
        department_id = request.POST.get('department')
        designation_id = request.POST.get('designation')
        joining = request.POST.get('joining')
        salary = request.POST.get('salary', '0').replace(',', '')
        bank_name = request.POST.get('bank_name', '').strip()
        bank_account = request.POST.get('bank_account', '').strip()
        profile_image = request.FILES.get('profile_image')


        
        
        # Validation
        errors = {}

          # === PROFILE IMAGE VALIDATION ===
        if profile_image:
            # Size check: 2MB max
            max_size = 2 * 1024 * 1024  # 2MB
            if profile_image.size > max_size:
                errors['profile_image'] = 'Profile image must be under 2MB'
            
            # Type check
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
            if profile_image.content_type not in allowed_types:
                errors['profile_image'] = 'Only JPG, PNG, WEBP images allowed'
        # =================================


        selected_user = None
        if not user_id:
            errors['user'] = 'User is required'
        else:
            selected_user = User.objects.filter(pk=user_id, role="employee").first()
            if selected_user is None:
                errors['user'] = 'Please select an employee user'
            elif Employee.objects.filter(user=selected_user).exists():
                errors['user'] = 'Employee profile already exists for this user'
        if not first_name:
            errors['first_name'] = 'First name is required'
        if not last_name:
            errors['last_name'] = 'Last name is required'
        if not phone:
            errors['phone'] = 'Phone is required'
        if not department_id:
            errors['department'] = 'Department is required'
        if not designation_id:
            errors['designation'] = 'Designation is required'
        if not joining:
            errors['joining'] = 'Joining date is required'
        if not salary:
            errors['salary'] = 'Salary is required'
        
        # Phone unique check
        if phone and Employee.objects.filter(phone=phone).exists():
            errors['phone'] = 'Phone number already exists'
        
        if errors:
            messages.error(request, 'Please correct the errors below.')
            context = {
                'errors': errors,
                'users': User.objects.filter(role="employee", employee_profile__isnull=True).order_by("email"),
                'departments': Department.objects.all(),
                'designations': Designation.objects.all(),

                
                'old_data': request.POST,
            }
            return render(request, 'admin/addemp.html', context)
        
        # Skills parse karo
        skills_list = []
        if skills_raw:
            skills_list = [s.strip() for s in skills_raw.split(',') if s.strip()]
        
        # Employee create karo
        employee = Employee.objects.create(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            profile_image=profile_image,
            address=address,
            date_of_birth=dob,
            emergency_contact=emergency_contact,
            bio=bio,
            skills=skills_list,
            employment_status=status,
            department_id=department_id,
            designation_id=designation_id,
            joining_date=joining,
            salary=salary,
            bank_name=bank_name,
            bank_account=bank_account,
        )
        
        messages.success(request, f'Employee {employee.full_name} added successfully!')
        return redirect('dashboard:employee_list')
    
    # GET request
    selected_user_id = request.GET.get("user", "")
    context = {
        'users': User.objects.filter(role="employee", employee_profile__isnull=True).order_by("email"),
        'departments': Department.objects.all(),
        'designations': Designation.objects.all(),
        'selected_user_id': selected_user_id,
    }
    return render(request, 'admin/addemp.html', context)




# ─── EDIT EMPLOYEE ───
@login_required
def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        # Direct POST data se update karo
        user_id = request.POST.get('user')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        dob = request.POST.get('dob') or None
        emergency_contact = request.POST.get('emergency_contact', '').strip()
        bio = request.POST.get('bio', '').strip()
        skills_raw = request.POST.get('skills', '')
        status = request.POST.get('status', 'ACTIVE').upper()
        department_id = request.POST.get('department')
        designation_id = request.POST.get('designation')
        joining = request.POST.get('joining')
        salary = request.POST.get('salary', '0').replace(',', '')
        bank_name = request.POST.get('bank_name', '').strip()
        bank_account = request.POST.get('bank_account', '').strip()
        profile_image = request.FILES.get('profile_image')
        
        # Validation
        errors = {}


         # === PROFILE IMAGE VALIDATION ===
        if profile_image:
            max_size = 2 * 1024 * 1024  # 2MB
            if profile_image.size > max_size:
                errors['profile_image'] = 'Profile image must be under 2MB'
            
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
            if profile_image.content_type not in allowed_types:
                errors['profile_image'] = 'Only JPG, PNG, WEBP images allowed'
        # =================================




        if not user_id:
            errors['user'] = 'User is required'
        if not first_name:
            errors['first_name'] = 'First name is required'
        if not last_name:
            errors['last_name'] = 'Last name is required'
        if not phone:
            errors['phone'] = 'Phone is required'
        if not department_id:
            errors['department'] = 'Department is required'
        if not designation_id:
            errors['designation'] = 'Designation is required'
        if not joining:
            errors['joining'] = 'Joining date is required'
        if not salary:
            errors['salary'] = 'Salary is required'
        
        # Phone unique check (current employee ko chhod ke)
        if phone and Employee.objects.filter(phone=phone).exclude(pk=pk).exists():
            errors['phone'] = 'Phone number already exists'
        
        if errors:
            messages.error(request, 'Please correct the errors below.')
            context = {
                'errors': errors,
                'employee': employee,
                'users': User.objects.filter(
                    Q(role="employee", employee_profile__isnull=True) | Q(pk=employee.user.pk)
                ).order_by("email"),
                'departments': Department.objects.all(),
                'designations': Designation.objects.all(),
                'old_data': request.POST,
            }
            return render(request, 'admin/editemp.html', context)
        
        # Skills parse karo
        skills_list = []
        if skills_raw:
            skills_list = [s.strip() for s in skills_raw.split(',') if s.strip()]
        
        # Update fields
        employee.user_id = user_id
        employee.first_name = first_name
        employee.last_name = last_name
        employee.phone = phone
        employee.address = address
        employee.date_of_birth = dob
        employee.emergency_contact = emergency_contact
        employee.bio = bio
        employee.skills = skills_list
        employee.employment_status = status
        employee.department_id = department_id
        employee.designation_id = designation_id
        employee.joining_date = joining
        employee.salary = salary
        employee.bank_name = bank_name
        employee.bank_account = bank_account




        
        # Profile image sirf agar nayi upload hui
        # if profile_image:
        #     employee.profile_image = profile_image
        
        # employee.save()




                # === PROFILE IMAGE HANDLE ===
        remove_photo = request.POST.get('remove_photo')
        
        if remove_photo:
            # Agar checkbox tick hai toh purani photo delete karo
            if employee.profile_image:
                employee.profile_image.delete(save=False)  # File system se delete
                employee.profile_image = None              # Database se hatao
        elif profile_image:
            # Nayi photo sirf tab lagao jab remove tick NAHI hai
            employee.profile_image = profile_image
        # =============================
        
        employee.save()






        
        messages.success(request, f'Employee {employee.full_name} updated successfully!')
        return redirect('dashboard:employee_list')
    
    # GET request
    # Skills ko comma separated string mein convert karo
    skills_str = ','.join(employee.skills) if isinstance(employee.skills, list) else ''
    
    context = {
        'employee': employee,
        'users': User.objects.filter(
            Q(role="employee", employee_profile__isnull=True) | Q(pk=employee.user.pk)
        ).order_by("email"),
        'departments': Department.objects.all(),
        'designations': Designation.objects.all(),
        'skills_str': skills_str,
    }
    return render(request, 'admin/editemp.html', context)


# ─── VIEW EMPLOYEE ───
@login_required
def view_employee(request, pk):
    employee = get_object_or_404(
        Employee.objects.select_related('user', 'department', 'designation'), 
        pk=pk
    )
    return render(request, 'admin/viewemp.html', {'employee': employee})




# ─── DELETE EMPLOYEE (AJAX) ───
@login_required
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        name = employee.full_name
        employee.delete()
        messages.success(request, f'Employee {name} deleted successfully!')
        return JsonResponse({'success': True, 'message': 'Employee deleted'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@login_required
def department_list(request):
    departments = Department.objects.all().order_by('-created_at')
    
    context = {
        'departments': departments,
        'current_date': timezone.now().strftime('%d %b %Y'),
    }
    return render(request, "admin/departments.html", context)

    
@login_required
def add_department(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        
        # Validation
        if not name:
            return JsonResponse({'success': False, 'error': 'Department name is required'})
        
        if Department.objects.filter(name__iexact=name).exists():
            return JsonResponse({'success': False, 'error': 'Department already exists'})
        
        # Create
        dept = Department.objects.create(name=name)
        
        
        return JsonResponse({
            'success': True,
            'message': 'Department added successfully',
            'department': {
                'id': dept.id,
                'name': dept.name,
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)




# ─── EDIT DEPARTMENT (AJAX) ───
@login_required
def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        
        # Validation
        if not name:
            return JsonResponse({'success': False, 'error': 'Department name is required'})
        
        if Department.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            return JsonResponse({'success': False, 'error': 'Department already exists'})
        
        # Update
        department.name = name
        department.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Department updated successfully',
            'department': {
                'id': department.id,
                'name': department.name,
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


# ─── DELETE DEPARTMENT (AJAX) ───
@login_required
def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        # Check: Koi employee is department mein hai kya?
        employee_count = Employee.objects.filter(department=department).count()
        
        if employee_count > 0:
            return JsonResponse({
                'success': False,
                'error': f'Cannot delete. {employee_count} employee(s) are assigned to this department.'
            })
        
        name = department.name
        department.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Department "{name}" deleted successfully'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def designation_list(request):
    designations = Designation.objects.select_related('department').all().order_by('-created_at')
    
    # Search filter (optional)
    search = request.GET.get('search', '')
    if search:
        designations = designations.filter(
            Q(title__icontains=search) |
            Q(department__name__icontains=search)
        )


    context = {
        'designations': designations,
        'departments': Department.objects.all().order_by('name'),
        'current_date': timezone.now().strftime('%d %b %Y'),
    }

    

  
    
    return render(request, "admin/designation.html", context)

    


@login_required
def add_designation(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        department_id = request.POST.get('department', '')
        
        # Validation
        if not title:
            return JsonResponse({'success': False, 'error': 'Designation title is required'})
        
        if Designation.objects.filter(title__iexact=title).exists():
            return JsonResponse({'success': False, 'error': 'Designation already exists'})
        
        # Create
        dept = None
        if department_id:
            dept = get_object_or_404(Department, pk=department_id)
        
        designation = Designation.objects.create(
            title=title,
            department=dept
        )

        
        return JsonResponse({
            'success': True,
            'message': 'Designation added successfully',
            'designation': {
                'id': designation.id,
                'title': designation.title,
                'department': designation.department.name if designation.department else '-',
                'department_id': designation.department_id,
            }
        })

      

    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


# ─── EDIT DESIGNATION (AJAX) ───
@login_required
def edit_designation(request, pk):
    designation = get_object_or_404(Designation, pk=pk)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        department_id = request.POST.get('department', '')
        
        # Validation
        if not title:
            return JsonResponse({'success': False, 'error': 'Designation title is required'})
        
        if Designation.objects.filter(title__iexact=title).exclude(pk=pk).exists():
            return JsonResponse({'success': False, 'error': 'Designation already exists'})
        
        # Update
        dept = None
        if department_id:
            dept = get_object_or_404(Department, pk=department_id)

            
        
        designation.title = title
        designation.department = dept
        designation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Designation updated successfully',
            'designation': {
                'id': designation.id,
                'title': designation.title,
                'department': designation.department.name if designation.department else '-',
                'department_id': designation.department_id,


            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


# ─── DELETE DESIGNATION (AJAX) ───
@login_required
def delete_designation(request, pk):
    designation = get_object_or_404(Designation, pk=pk)

   
    if request.method == 'POST':
        # Check: Koi employee is designation mein hai kya?
        from employees.models import Employee
        employee_count = Employee.objects.filter(designation=designation).count()
        
        if employee_count > 0:
            return JsonResponse({
                'success': False,
                'error': f'Cannot delete. {employee_count} employee(s) assigned to this designation.'
            })
        
        title = designation.title
        designation.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Designation "{title}" deleted'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


from attendance.services import mark_absent_employees


def is_admin(user):
    """Check if user is admin/staff."""
    return user.is_staff or user.is_superuser


def is_weekly_off(date_obj):
    """
    Check if given date is a weekly off.
    Saturday (5) and Sunday (6) are both weekly off.
    """
    return date_obj.weekday() in [5, 6]  # Saturday=5, Sunday=6






@login_required
@user_passes_test(is_admin)
def attendance_list(request):
    """
    Admin Attendance Dashboard.
    Renders the attendance management page with:
    - Summary cards (Present, Absent, Leave, Half Day) for TODAY
    - Attendance register table for all employees for TODAY
    """
    now = timezone.localtime()
    today = timezone.localdate()
    # today = timezone.now().date()
    today_str = today.strftime("%Y-%m-%d")
    day_name = today.strftime("%A")


    if now.hour >= 18:
        mark_absent_employees(target_date=today)

    # today_str = today.strftime("%Y-%m-%d")
    # day_name = today.strftime("%A")

    # Get all active employees with their department and designation



    # employees = Employee.objects.filter(
    #     employment_status="ACTIVE"
    # ).select_related(
    #     'department', 
    #     'designation', 
    #     'user'
    # ).order_by('first_name', 'last_name')




    employees = Employee.objects.filter(
        employment_status="ACTIVE"
    ).select_related('department', 'designation', 'user').order_by('first_name', 'last_name')



    # Get today's attendance records for all employees


    # today_attendance = Attendance.objects.filter(
    #     date=today
    # ).select_related('employee', 'leave_request')


    today_attendance = Attendance.objects.filter(date=today).select_related('employee', 'leave_request')


    # Get approved leaves for today (these override attendance status)


    # today_leaves = Leave.objects.filter(
    #     start_date__lte=today,
    #     end_date__gte=today,
    #     status='approved'
    # ).select_related('employee')


    today_leaves = Leave.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        status='approved'
    ).select_related('employee', 'employee__department', 'employee__designation')





    # Build lookup dicts for fast access (employee_id -> record)
    attendance_map = {}
    for att in today_attendance:
        attendance_map[att.employee_id] = att

    leave_map = {}
    for leave in today_leaves:
        leave_map[leave.employee_id] = leave

    today_punch_sessions = PunchSession.objects.filter(date=today).select_related('employee')

    punch_map = {}
    for ps in today_punch_sessions:
        if ps.employee_id not in punch_map:
            punch_map[ps.employee_id] = ps



    

    # Build attendance rows for the table
    attendance_rows = []
    summary_counts = {
        'present': 0,
        'absent': 0,
        'leave': 0,
        'half_day': 0,
    }

    for emp in employees:
        joining_date = emp.joining_date
        not_yet_joined = today < joining_date

        # Determine effective status
        # effective_status = None
        working_hours = 0
        status = None

        if not_yet_joined:
            status = 'not_joined'
            working_hours = 0
        else:
            # Priority 1: Approved leave (highest priority)
            # Priority 1: Approved leave (Chhutti hai toh LEAVE)
            if emp.id in leave_map:
                status = 'leave'
                working_hours = 0

            # Priority 2: Explicit attendance record from PunchSession/Attendance table
            elif emp.id in attendance_map:
                att = attendance_map[emp.id]
                status = att.status
                working_hours = float(att.working_hours)

            # 🟢 [NAYA ADD KARO]: Priority 3 - Punch In Tracking
            elif emp.id in punch_map:
                ps = punch_map[emp.id]
                status = 'present'  # Punch in kiya hai toh PRESENT dikhao!
                working_hours = float(getattr(ps, 'total_hours', 0) or 0)



            # Priority 3: Fallback (Saturday & Sunday = weekly_off, else absent)
            else:
                if is_weekly_off(today):
                    status = 'weekly_off'
                else:
            # 10 AM se Shaam 6 PM ke beech (11 baje, 2 baje, etc.) -> Pending (Not Marked)
                    if now.hour < 18:
                        status = 'pending'
                    # Shaam 6 PM ke baad -> Absent
                    else:
                        status = 'absent'

                # else:
                #     effective_status = 'absent'
                # working_hours = 0
                    working_hours = 0
                # status = effective_status

            # Count for summary cards (only these 4 statuses shown on cards)
            if status in summary_counts:
                summary_counts[status] += 1

        attendance_rows.append({
            'employee': emp,
            'date': today_str,
            'day': day_name,
            'status': status,
            'working_hours': working_hours,
            'not_yet_joined': not_yet_joined,
        })

    context = {
        'attendance_rows': attendance_rows,
        'summary_counts': summary_counts,
        'today_date': today,
        'today_display': today.strftime("%d %b %Y"),  # e.g., "24 Jun 2026"
    }

    return render(request, "admin/aattendance.html", context)


@login_required
@user_passes_test(is_admin)
def employee_attendance_calendar(request, employee_id):
    # print(f"DEBUG: employee_id={employee_id}")  # <-- ADD KAR
    """
    AJAX endpoint: Returns month-wise attendance data for an employee.
    Used by the modal calendar view when admin clicks "View" button.

    Query params:
        year: int (default current year)
        month: int (default current month, 1-12)

    Returns JSON:
        {
            employee: { id, name, initials, employee_code, department, designation, email, joining_date },
            year: 2026,
            month: 6,
            month_name: "June",
            days_in_month: 30,
            first_day_of_week: 0,  // Python weekday (0=Monday)
            calendar_days: [
                { day: 1, date: "2026-06-01", status: "present", short_status: "P", dot_class: "dot-present", is_today: false, ... },
                ...
            ],
            summary: { present: 15, absent: 2, leave: 3, half_day: 1 }
        }
    """
    # employee = get_object_or_404(Employee, id=employee_id)
    employee = get_object_or_404(
    Employee.objects.select_related('department', 'designation'), 
    id=employee_id
    )

    try:
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
        if not (1 <= month <= 12):
            month = timezone.now().month
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month


    # today = timezone.now().date()
    # today = timezone.localdate()

    now = timezone.localtime()  # <-- YE LINE ADD KARO
    today = now.date()
    joining_date = employee.joining_date

    # Get days in month
    days_in_month = monthrange(year, month)[1]

    # Get all attendance records for this employee in this month
    month_start = datetime(year, month, 1).date()
    month_end = datetime(year, month, days_in_month).date()

    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__gte=month_start,
        date__lte=month_end
    )

    # Get approved leaves for this employee in this month
    approved_leaves = Leave.objects.filter(
        employee=employee,
        status='approved',
        start_date__lte=month_end,
        end_date__gte=month_start
    )

    # 🟢 [CHANGE HERE]: Punch sessions fetch karo
    punch_sessions = PunchSession.objects.filter(
        employee=employee,
        date__gte=month_start,
        date__lte=month_end
    )







    # Build attendance lookup by date (YYYY-MM-DD -> Attendance object)
    att_map = {}
    for att in attendance_records:
        att_map[att.date.strftime("%Y-%m-%d")] = att


    # 🟢 [CHANGE HERE]: Punch map banao fast lookup ke liye
    punch_map = {}
    for ps in punch_sessions:
        punch_map[ps.date.strftime("%Y-%m-%d")] = ps


    

    # Build leave lookup by date (YYYY-MM-DD -> Leave object)
    # Expand each leave's date range into individual days
    leave_map = {}
    for leave in approved_leaves:
        leave_start = leave.start_date
        leave_end = leave.end_date
        current = leave_start
        while current <= leave_end:
            leave_map[current.strftime("%Y-%m-%d")] = leave
            current += timedelta(days=1)

    # Build calendar days array
    calendar_days = []
    summary_counts = {
        'present': 0,
        'absent': 0,
        'leave': 0,
        'half_day': 0,
    }

    for day in range(1, days_in_month + 1):
        date_obj = datetime(year, month, day).date()
        date_key = date_obj.strftime("%Y-%m-%d")
        day_name = date_obj.strftime("%A")

        is_today = date_obj == today
        is_future = date_obj > today
        is_before_joining = (joining_date is not None) and (date_obj < joining_date)
        # is_before_joining = date_obj < joining_date

        # Determine effective status based on priority rules
        if is_before_joining:
            status = 'before_joining'
            short_status = ''
            dot_class = ''
        elif is_future:
            status = 'future'
            short_status = ''
            dot_class = ''
        else:
            # Priority 1: Approved leave (highest priority)
            if date_key in leave_map:
                effective_status = 'leave'
            # Priority 2: Explicit attendance record from Attendance table
            elif date_key in att_map:
                effective_status = att_map[date_key].status

            # 🟢 [CHANGE HERE]: Priority 3 - Punch In Tracking
            elif date_key in punch_map:
                effective_status = 'present'  # Punch In kiya hai toh PRESENT dikhao!


            # Priority 3: Fallback (Saturday & Sunday = weekly_off, else absent)
            else:
                if is_weekly_off(date_obj):
                    effective_status = 'weekly_off'

                else:
                    # Aaj ka din hai aur shaam 6 baje se pehle -> Pending, baaki cases me Absent
                    if is_today and now.hour < 18:
                        effective_status = 'pending'
                    else:
                        effective_status = 'absent'

                
                # else:
                #     effective_status = 'absent'

            status = effective_status

            # Status mapping for frontend badges/dots
            status_short_map = {
                'present': 'P',
                'absent': 'A',
                'half_day': 'HD',
                'leave': 'L',
                'weekly_off': 'WO',
                'holiday': 'H',
                'pending': '-',
            }

            status_dot_map = {
                'present': 'dot-present',
                'absent': 'dot-absent',
                'half_day': 'dot-half_day',
                'leave': 'dot-leave',
                'weekly_off': 'dot-weekly_off',
                'holiday': 'dot-holiday',
                'pending': 'dot-pending',
            }

            short_status = status_short_map.get(status, '')
            dot_class = status_dot_map.get(status, '')

            # Count for summary (only employed, non-future days)
            if status in summary_counts:
                summary_counts[status] += 1

        calendar_days.append({
            'day': day,
            'date': date_key,
            'day_name': day_name,
            'status': status,
            'short_status': short_status,
            'dot_class': dot_class,
            'is_today': is_today,
            'is_future': is_future,
            'is_before_joining': is_before_joining,
        })

    # Employee info for modal header
    employee_info = {
        'id': employee.id,
        'name': employee.full_name,
        'initials': get_initials(employee.first_name, employee.last_name),
        'employee_code': employee.employee_code,
        'department': employee.department.name if employee.department else '-',
        'designation': employee.designation.title if employee.designation else '-',
        'email': employee.email,
        'joining_date': joining_date.strftime("%d %b %Y") if joining_date else '-',
    }

    data = {
        'employee': employee_info,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'days_in_month': days_in_month,
        'first_day_of_week': monthrange(year, month)[0],  # Python weekday: 0=Monday, 6=Sunday
        'calendar_days': calendar_days,
        'summary': summary_counts,
    }

    return JsonResponse(data)


def get_initials(first_name, last_name):
    """Helper to get initials from first and last name."""
    first = first_name[0] if first_name else ''
    last = last_name[0] if last_name else ''
    return (first + last).upper()


def punch_sessions(request):
    return render(request, "admin/punch_sessions.html")



from datetime import time  # ← NAYA IMPORT
from Punch.services import auto_close_session  # ← NAYA IMPORT


# # API view - Sirf AAJ ka data (current date)
class PunchSessionListAPIView(generics.ListAPIView):
    serializer_class = PunchSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # today = timezone.now().date()
        today = timezone.localdate()
        now = timezone.localtime()  # ← ADD


        #  # ===== LAZY AUTO-CLOSE START =====
        # # 6:10 PM ke baad aaj ke bhoole hue employees ko 6 PM pe close karo
        # if now.time() >= time(18, 10):
        #     stale_today = PunchSession.objects.filter(
        #         status="active",
        #         date=today,
        #         punch_in_at__hour__lt=18,
        #     )
        #     for session in stale_today:
        #         close_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
        #         auto_close_session(session, close_time)
        # # ===== LAZY AUTO-CLOSE END =====




        
        queryset = PunchSession.objects.select_related(
            'employee',
            'employee__department',
            'attendance'
        ).filter(
            date=today
        ).order_by('-punch_in_at')

        status = self.request.query_params.get('status')
        search = self.request.query_params.get('search')

        if status:
            queryset = queryset.filter(status=status.lower())
        if search:
            queryset = queryset.filter(
                Q(employee__full_name__icontains=search) |
                Q(employee__employee_code__icontains=search)  # <-- employee_code fix
            )

        return queryset


# # API view - Sirf AAJ ka data (current date)
# class PunchSessionListAPIView(generics.ListAPIView):
#     serializer_class = PunchSessionSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         today = timezone.now().date()
        
#         # Sirf aaj ka data - jisne punch in kiya hai
#         queryset = PunchSession.objects.select_related(
#             'employee',
#             'employee__department',
#             'attendance'
#         ).filter(
#             date=today  # Sirf current date
#         ).order_by('-punch_in_at')

#         # Optional filters from query params
#         status = self.request.query_params.get('status')
#         search = self.request.query_params.get('search')

#         if status:
#             queryset = queryset.filter(status=status.lower())
#         if search:
#             queryset = queryset.filter(
#                 Q(employee__full_name__icontains=search) |
#                 Q(employee__emp_code__icontains=search)
#             )

#         return queryset


def project_list(request):
    return render(request, "admin/project.html")


# ═══════════════════════════════════════════════════════════════════════
# API VIEWS (JSON data dete hain - DRF)
# ═══════════════════════════════════════════════════════════════════════

# ── Punch Sessions API ──
class PunchSessionListAPIView(generics.ListAPIView):
    serializer_class = PunchSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        today = timezone.now().date()
        queryset = PunchSession.objects.select_related(
            'employee', 'employee__department', 'attendance'
        ).filter(date=today).order_by('-punch_in_at')

        status = self.request.query_params.get('status')
        search = self.request.query_params.get('search')

        if status:
            queryset = queryset.filter(status=status.lower())
        if search:
            queryset = queryset.filter(
                Q(employee__full_name__icontains=search) |
                Q(employee__employee_code__icontains=search)
            )
        return queryset


# ── Project APIs ──
class ProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.select_related(
            'client', 'created_by'
        ).prefetch_related('employees').all().order_by("-created_at")
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status.lower())
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()


class ClientListAPIView(generics.ListAPIView):
    serializer_class = ClientDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all().order_by("-id")


class EmployeeListAPIView(generics.ListAPIView):
    serializer_class = EmployeeMiniSerializer
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.select_related('department').all()


class UserListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.all()
    
    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        data = [{"id": u.id, "email": u.email} for u in users]
        return Response(data)


from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser


def client_list(request):
    return render(request, "admin/clients.html")





# ─── LIST ALL CLIENTS ───
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser]) 
def client_get_all(request):
    """GET /dashboard/api/clients/"""
    clients = Client.objects.all().order_by('-created_at')
    serializer = ClientDetailSerializer(clients, many=True, context={'request': request})
    return Response(serializer.data)


# ─── CREATE CLIENT ───
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser]) 
@parser_classes([MultiPartParser, FormParser])
def client_create(request):
    """POST /dashboard/api/clients/create/"""
    serializer = ClientDetailSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── GET SINGLE CLIENT ───
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser]) 
def client_get_one(request, pk):
    """GET /dashboard/api/clients/<pk>/"""
    client = get_object_or_404(Client, pk=pk)
    serializer = ClientDetailSerializer(client, context={'request': request})
    return Response(serializer.data)


# ─── UPDATE CLIENT ───
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def client_update(request, pk):
    """PUT /dashboard/api/clients/<pk>/update/"""
    client = get_object_or_404(Client, pk=pk)
    serializer = ClientDetailSerializer(client, data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── DELETE CLIENT ───
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser]) 
def client_delete(request, pk):
    """DELETE /dashboard/api/clients/<pk>/delete/"""
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    return Response({'message': 'Client deleted successfully'}, status=status.HTTP_204_NO_CONTENT)








# from io import BytesIO
# from django.http import HttpResponse
# from django.template.loader import get_template
# from django.shortcuts import render, get_object_or_404
# from django.conf import settings
# from xhtml2pdf import pisa
# from rest_framework.decorators import api_view, permission_classes, parser_classes
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework import status
# from rest_framework.response import Response
# from projects.models import ServiceCatalog, Invoice, InvoiceItem
# from projects.serializers import ServiceCatalogSerializer, InvoiceSerializer, InvoiceItemSerializer








import os
import logging
from io import BytesIO
from decimal import Decimal

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template

from xhtml2pdf import pisa
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.response import Response

from projects.models import ServiceCatalog, Invoice, InvoiceItem
from projects.serializers import ServiceCatalogSerializer, InvoiceSerializer, InvoiceItemSerializer

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# TEMPLATE VIEWS
# ═══════════════════════════════════════════════════════════════════════

def service_list(request):
    return render(request, "admin/services.html")


def invoice_list(request):
    return render(request, "admin/invoices.html")


def invoice_item_list(request):
    return render(request, "admin/invoice_items.html")


# ═══════════════════════════════════════════════════════════════════════
# SERVICE CATALOG APIs
# ═══════════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def service_get_all(request):
    services = ServiceCatalog.objects.all().order_by('-created_at')
    serializer = ServiceCatalogSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def service_create(request):
    serializer = ServiceCatalogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def service_get_one(request, pk):
    service = get_object_or_404(ServiceCatalog, pk=pk)
    serializer = ServiceCatalogSerializer(service)
    return Response(serializer.data)








@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def service_update(request, pk):
    service = get_object_or_404(ServiceCatalog, pk=pk)
    serializer = ServiceCatalogSerializer(service, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def service_delete(request, pk):
    service = get_object_or_404(ServiceCatalog, pk=pk)
    service.delete()
    return Response({'message': 'Service deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# ═══════════════════════════════════════════════════════════════════════
# INVOICE APIs
# ═══════════════════════════════════════════════════════════════════════

# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_get_all(request):
#     invoices = Invoice.objects.select_related('client').prefetch_related('items').order_by('-issue_date')
#     serializer = InvoiceSerializer(invoices, many=True, context={'request': request})
#     return Response(serializer.data)





# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def invoice_get_all(request):
#     try:
#         show_deleted = request.GET.get('show_deleted', 'false').lower() == 'true'
        
#         invoices = (Invoice.objects
#                     .select_related('client')
#                     .prefetch_related('items')
#                     .filter(is_deleted=show_deleted)
#                     .order_by('-issue_date', '-id'))

#         serializer = InvoiceSerializer(invoices, many=True, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except Exception as e:
#         logger.exception("invoice_get_all failed")
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def invoice_get_all(request):
#     try:
#         show_deleted = request.GET.get('show_deleted', 'false').lower() == 'true'
#         search_query = request.GET.get('search', '').strip()
#         status_filter = request.GET.get('status', '').strip()

#         invoices = Invoice.objects.select_related('client', 'deleted_by').prefetch_related('items')
        
#         # Soft deleted / Active invoices toggle
#         invoices = invoices.filter(is_deleted=show_deleted)

#         # Search by invoice_number or client company_name
#         if search_query:
#             invoices = invoices.filter(
#                 Q(invoice_number__icontains=search_query) |
#                 Q(client__company_name__icontains=search_query)
#             )

#         # Status filter
#         if status_filter:
#             invoices = invoices.filter(status=status_filter)

#         invoices = invoices.order_by('-issue_date', '-id')

#         serializer = InvoiceSerializer(invoices, many=True, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except Exception as e:
#         logger.exception("invoice_get_all failed")
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)












@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_get_all(request):
    try:
        show_deleted = request.GET.get('show_deleted', 'false').lower() == 'true'
        search_query = request.GET.get('search', '').strip()
        status_filter = request.GET.get('status', '').strip()

        invoices = Invoice.objects.select_related('client', 'deleted_by').prefetch_related('items')
        
        # Filter active vs deleted
        invoices = invoices.filter(is_deleted=show_deleted)

        if search_query:
            invoices = invoices.filter(
                Q(invoice_number__icontains=search_query) |
                Q(client__company_name__icontains=search_query)
            )

        if status_filter:
            invoices = invoices.filter(status=status_filter)

        invoices = invoices.order_by('-issue_date', '-id')

        serializer = InvoiceSerializer(invoices, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception("invoice_get_all failed")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)











# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_create(request):
#     serializer = InvoiceSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_create(request):
#     serializer = InvoiceSerializer(data=request.data, context={'request': request})
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)









@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def invoice_create(request):
    serializer = InvoiceSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






















# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_get_one(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     serializer = InvoiceSerializer(invoice, context={'request': request})
#     return Response(serializer.data)





# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_get_one(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     serializer = InvoiceSerializer(invoice, context={'request': request})
#     return Response(serializer.data)









@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def invoice_get_one(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    serializer = InvoiceSerializer(invoice, context={'request': request})
    return Response(serializer.data)

















# @api_view(['PUT'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_update(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     if invoice.is_locked:
#         return Response(
#             {'detail': f"'{invoice.get_status_display()}' invoice edit nahi ho sakti."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
















# @api_view(['PUT'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_update(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     if invoice.is_locked:
#         return Response(
#             {'detail': f"'{invoice.get_status_display()}' invoice edit nahi ho sakti."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     serializer = InvoiceSerializer(invoice, data=request.data, partial=True, context={'request': request})
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






# @api_view(['PUT'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_update(request, pk):
#     """Full update rights given to Admin for any status"""
#     invoice = get_object_or_404(Invoice, pk=pk)
#     serializer = InvoiceSerializer(invoice, data=request.data, partial=True, context={'request': request})
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)












@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def invoice_update(request, pk):
    """Admin ke paas active, paid, cancelled har invoice number/details change karne ki full power hai"""
    invoice = get_object_or_404(Invoice, pk=pk)
    serializer = InvoiceSerializer(invoice, data=request.data, partial=True, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



























# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_delete(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
    
#     if invoice.is_locked:
#         return Response(
#             {'detail': 'Paid/Cancelled invoice delete nahi ho sakti.'},
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
#     # Direct DB delete ki jagah Soft Delete
#     invoice.soft_delete(user=request.user)
#     return Response({'message': f'Invoice {invoice.invoice_number} marked as deleted.'}, status=status.HTTP_200_OK)


















# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_delete(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
    
#     if invoice.is_locked:
#         return Response(
#             {'detail': 'Paid/Cancelled invoice delete nahi ho sakti.'},
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
#     invoice.soft_delete(user=request.user)
#     return Response({'message': f'Invoice {invoice.invoice_number} marked as deleted.'}, status=status.HTTP_200_OK)











@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def invoice_delete(request, pk):
    """Admin can soft-delete any invoice (Paid/Cancelled/Draft)"""
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.soft_delete(user=request.user)
    return Response({'message': f'Invoice {invoice.invoice_number} successfully deleted.'}, status=status.HTTP_200_OK)

























































# ═══════════════════════════════════════════════════════════════════════
# INVOICE ITEM APIs
# ═══════════════════════════════════════════════════════════════════════



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def invoice_item_get_all(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    items = invoice.items.select_related('project', 'service').all()
    serializer = InvoiceItemSerializer(items, many=True)
    return Response(serializer.data)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_item_create(request, invoice_id):
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
#     if invoice.is_locked:
#         return Response(
#             {'detail': 'Paid/Cancelled invoice mein item add nahi ho sakta.'},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     data = request.data.copy()
#     data['invoice'] = invoice.id
#     serializer = InvoiceItemSerializer(data=data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

















# views.py
# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_item_create(request):
#     # Request body se invoice ID fetch karein
#     invoice_id = request.data.get('invoice')
#     if not invoice_id:
#         return Response({'detail': 'Invoice ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
    
#     # Optional: Agar locked restriction hatani ho toh condition comment kar dein
#     if invoice.is_locked:
#         return Response(
#             {'detail': 'Paid/Cancelled invoice mein item add nahi ho sakta.'},
#             status=status.HTTP_400_BAD_REQUEST
#         )
        
#     serializer = InvoiceItemSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)










@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def invoice_item_create(request):
    invoice_id = request.data.get('invoice')
    if not invoice_id:
        return Response({'detail': 'Invoice ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    if getattr(invoice, 'is_locked', False):
        return Response(
            {'detail': 'Paid/Cancelled invoice mein item add nahi ho sakta.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    serializer = InvoiceItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





























@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def invoice_item_get_one(request, pk):
    item = get_object_or_404(InvoiceItem, pk=pk)
    serializer = InvoiceItemSerializer(item)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def invoice_item_update(request, pk):
    item = get_object_or_404(InvoiceItem, pk=pk)
    if item.invoice.is_locked:
        return Response(
            {'detail': 'Paid/Cancelled invoice ke items edit nahi ho sakte.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer = InvoiceItemSerializer(item, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    print("Serializer Validation Errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def invoice_item_delete(request, pk):
    item = get_object_or_404(InvoiceItem, pk=pk)
    if item.invoice.is_locked:
        return Response(
            {'detail': 'Paid/Cancelled invoice ke items delete nahi ho sakte.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    item.delete()
    return Response({'message': 'Item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════════
# PDF GENERATION HELPERS
# ═══════════════════════════════════════════════════════════════════════

def fetch_resources(uri, rel):
    """Static URLs ko absolute system path mein convert karta hai (xhtml2pdf ke liye)."""
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
        if os.path.exists(path):
            return path
        result = finders.find(uri.replace(settings.STATIC_URL, ""))
        if result:
            return result
    return uri


_ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
         "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
         "Seventeen", "Eighteen", "Nineteen"]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _two_digit_words(n):
    if n < 20:
        return _ONES[n]
    return (_TENS[n // 10] + (" " + _ONES[n % 10] if n % 10 else "")).strip()


def amount_in_words(amount):
    amount = Decimal(amount).quantize(Decimal("0.01"))
    rupees = int(amount)
    paise = int((amount - rupees) * 100)

    if rupees == 0 and paise == 0:
        return "Zero Rupees Only"

    parts = []
    crore = rupees // 10_000_000
    lakh = (rupees // 100_000) % 100
    thousand = (rupees // 1000) % 100
    hundred = (rupees // 100) % 10
    rest = rupees % 100

    if crore:
        parts.append(_two_digit_words(crore) + " Crore")
    if lakh:
        parts.append(_two_digit_words(lakh) + " Lakh")
    if thousand:
        parts.append(_two_digit_words(thousand) + " Thousand")
    if hundred:
        parts.append(_ONES[hundred] + " Hundred")
    if rest:
        parts.append(_two_digit_words(rest))

    words = " ".join(parts) + " Rupees"
    if paise:
        words += f" and {paise:02d} Paise"
    return words + " Only"


def get_company_context():
    return {
        "company_name": getattr(settings, "COMPANY_NAME", "PRESTIGIEUX MEDIATECH PVT. LTD."),
        "company_address": getattr(settings, "COMPANY_ADDRESS", ""),
        "company_phone": getattr(settings, "COMPANY_PHONE", ""),
        "company_email": getattr(settings, "COMPANY_EMAIL", ""),
        "company_gstin": getattr(settings, "COMPANY_GSTIN", ""),
        "bank_name": getattr(settings, "BANK_NAME", ""),
        "bank_account_name": getattr(settings, "BANK_ACCOUNT_NAME", ""),
        "bank_account_no": getattr(settings, "BANK_ACCOUNT_NO", ""),
        "bank_ifsc": getattr(settings, "BANK_IFSC", ""),
    }


# @login_required
# def invoice_pdf_view(request, pk):
#     if not request.user.is_staff:
#         raise PermissionDenied

#     invoice = get_object_or_404(Invoice, pk=pk)
#     items = invoice.items.select_related("project", "service").all()
#     template = get_template("admin/invoice_pdf.html")

#     notes_list = []
#     if invoice.notes:
#         raw_lines = invoice.notes.split('\n')
#         for line in raw_lines:
#             clean_line = line.strip().lstrip("•-* .")
#             if clean_line:
#                 notes_list.append(clean_line)

#     context = {
#         "invoice": invoice,
#         "items": items,
#         "notes_list": notes_list,
#         "amount_words": amount_in_words(invoice.total_amount),
#         **get_company_context(),
#     }

#     html = template.render(context)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=fetch_resources)

#     if not pdf.err:
#         response = HttpResponse(result.getvalue(), content_type="application/pdf")
#         response["Content-Disposition"] = f'inline; filename="{invoice.invoice_number or "invoice"}.pdf"'
#         return response

#     return HttpResponse("PDF generation failed", status=400)












from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from playwright.sync_api import sync_playwright


# @login_required
# def invoice_pdf_view(request, pk):
#     if not request.user.is_staff:
#         raise PermissionDenied

#     invoice = get_object_or_404(Invoice, pk=pk)
#     items = invoice.items.select_related("project", "service").all()
#     template = get_template("admin/invoice_pdf.html")

#     notes_list = []
#     if invoice.notes:
#         raw_lines = invoice.notes.split("\n")
#         for line in raw_lines:
#             clean_line = line.strip().lstrip("•-* .")
#             if clean_line:
#                 notes_list.append(clean_line)

#     context = {
#         "invoice": invoice,
#         "items": items,
#         "notes_list": notes_list,
#         "amount_words": amount_in_words(invoice.total_amount),
#         **get_company_context(),
#     }

#     # Render HTML template with context
#     html_content = template.render(context, request=request)

#     # Generate PDF using Playwright (Real Chromium Browser)
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()

#         # Absolute URL for images & static assets
#         base_url = request.build_absolute_uri("/")
#         page.set_content(html_content, wait_until="networkidle", base_url=base_url)

#         # PDF output settings
#         pdf_bytes = page.pdf(
#             format="A4",
#             print_background=True,
#             margin={
#                 "top": "10mm",
#                 "bottom": "10mm",
#                 "left": "14mm",
#                 "right": "14mm",
#             },
#         )
#         browser.close()

#     response = HttpResponse(pdf_bytes, content_type="application/pdf")
#     response["Content-Disposition"] = (
#         f'inline; filename="{invoice.invoice_number or "invoice"}.pdf"'
#     )
#     return response








@login_required
def invoice_pdf_view(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied

    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.select_related("project", "service").all()
    template = get_template("admin/invoice_pdf.html")

    notes_list = []
    if invoice.notes:
        raw_lines = invoice.notes.split("\n")
        for line in raw_lines:
            clean_line = line.strip().lstrip("•-* .")
            if clean_line:
                notes_list.append(clean_line)

    context = {
        "invoice": invoice,
        "items": items,
        "notes_list": notes_list,
        "amount_words": amount_in_words(invoice.total_amount),
        **get_company_context(),
    }

    html_content = template.render(context, request=request)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Correct set_content call
        page.set_content(html_content, wait_until="networkidle")

        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={
                "top": "10mm",
                "bottom": "10mm",
                "left": "14mm",
                "right": "14mm",
            },
        )
        browser.close()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="{invoice.invoice_number or "invoice"}.pdf"'
    )
    return response








































































# @api_view(['PUT'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def invoice_item_update(request, pk):
#     item = get_object_or_404(InvoiceItem, pk=pk)
#     serializer = InvoiceItemSerializer(item, data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)















# ═══════════════════════════════════════════════════════════════════════
# PDF GENERATION
# ═══════════════════════════════════════════════════════════════════════

# def invoice_pdf_view(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     items = invoice.items.select_related('project', 'service').all()
#     template = get_template('admin/invoice_pdf.html')
#     html = template.render({
#         'invoice': invoice,
#         'items': items,
#         'company_name': getattr(settings, 'COMPANY_NAME', 'YOUR COMPANY'),
#         'company_address': getattr(settings, 'COMPANY_ADDRESS', ''),
#         'company_phone': getattr(settings, 'COMPANY_PHONE', ''),
#     })
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
#     if not pdf.err:
#         response = HttpResponse(result.getvalue(), content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
#         return response
#     return HttpResponse("PDF generation failed", status=400)

























# def invoice_pdf_view(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     items = invoice.items.select_related('project', 'service').all()
#     template = get_template('admin/invoice_pdf.html')
#     html = template.render({
#         'invoice': invoice,
#         'items': items,
#         'company_name': getattr(settings, 'COMPANY_NAME', 'YOUR COMPANY'),
#         'company_address': getattr(settings, 'COMPANY_ADDRESS', ''),
#         'company_phone': getattr(settings, 'COMPANY_PHONE', ''),
#     })
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
#     if not pdf.err:
#         response = HttpResponse(result.getvalue(), content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
#         return response
#     return HttpResponse("PDF generation failed", status=400)







# import os
# from io import BytesIO
# from django.conf import settings
# from django.contrib.staticfiles import finders
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
# from django.template.loader import get_template
# from xhtml2pdf import pisa


# # 1. Static Files Helper (Local + Production safe)
# def fetch_resources(uri, rel):
#     """Convert HTML static URLs to absolute system paths for xhtml2pdf."""
#     if uri.startswith(settings.STATIC_URL):
#         # Production (after collectstatic)
#         path = os.path.join(
#             settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, "")
#         )
#         if os.path.exists(path):
#             return path

#         # Local Development (finders search)
#         result = finders.find(uri.replace(settings.STATIC_URL, ""))
#         if result:
#             return result
#     return uri


# # 2. Updated Invoice PDF View
# def invoice_pdf_view(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     items = invoice.items.select_related("project", "service").all()
#     template = get_template("admin/invoice_pdf.html")

#     html = template.render(
#         {
#             "invoice": invoice,
#             "items": items,
#             "company_name": getattr(
#                 settings, "COMPANY_NAME", "PRESTIGIEUX MEDIATECH PVT. LTD."
#             ),
#             "company_address": getattr(settings, "COMPANY_ADDRESS", ""),
#             "company_phone": getattr(settings, "COMPANY_PHONE", ""),
#         }
#     )

#     result = BytesIO()

#     # Pass link_callback here
#     pdf = pisa.pisaDocument(
#         BytesIO(html.encode("UTF-8")), result, link_callback=fetch_resources
#     )

#     if not pdf.err:
#         response = HttpResponse(
#             result.getvalue(), content_type="application/pdf"
#         )
#         response["Content-Disposition"] = (
#             f'attachment; filename="{invoice.invoice_number}.pdf"'
#         )
#         return response

#     return HttpResponse("PDF generation failed", status=400)

































# import os
# from io import BytesIO
# from django.conf import settings
# from django.contrib.staticfiles import finders
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
# from django.template.loader import get_template
# from xhtml2pdf import pisa
# from projects.models import Invoice  # Aapka model import


# # 1. Static Files Helper (Local + Production safe)
# def fetch_resources(uri, rel):
#     """Convert HTML static URLs to absolute system paths for xhtml2pdf."""
#     if uri.startswith(settings.STATIC_URL):
#         path = os.path.join(
#             settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, "")
#         )
#         if os.path.exists(path):
#             return path

#         result = finders.find(uri.replace(settings.STATIC_URL, ""))
#         if result:
#             return result
#     return uri


# # 2. Updated Invoice PDF View
# def invoice_pdf_view(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     items = invoice.items.select_related("project", "service").all()
#     template = get_template("admin/invoice_pdf.html")

#     # --- NOTES TO BULLET LIST PARSING ---
#     notes_list = []
#     if invoice.notes:
#         # Har new line ya dot ko clean list item banayega
#         raw_lines = invoice.notes.split('\n')
#         for line in raw_lines:
#             clean_line = line.strip().lstrip("•-* .")
#             if clean_line:
#                 notes_list.append(clean_line)

#     html = template.render(
#         {
#             "invoice": invoice,
#             "items": items,
#             "notes_list": notes_list,  # Formatted Bullet Items
#             "company_name": getattr(
#                 settings, "COMPANY_NAME", "PRESTIGIEUX MEDIATECH PVT. LTD."
#             ),
#             "company_address": getattr(settings, "COMPANY_ADDRESS", ""),
#             "company_phone": getattr(settings, "COMPANY_PHONE", ""),
#         }
#     )

#     result = BytesIO()

#     pdf = pisa.pisaDocument(
#         BytesIO(html.encode("UTF-8")), result, link_callback=fetch_resources
#     )

#     if not pdf.err:
#         response = HttpResponse(
#             result.getvalue(), content_type="application/pdf"
#         )
#         response["Content-Disposition"] = (
#             f'inline; filename="{invoice.invoice_number}.pdf"'
#         )
#         return response

#     return HttpResponse("PDF generation failed", status=400)
















# def payroll_list(request):
#     return render(request, "admin/payroll.html")






# logger = logging.getLogger(__name__)










# MONTHS = [
#     {"id": 1, "name": "January"}, {"id": 2, "name": "February"},
#     {"id": 3, "name": "March"}, {"id": 4, "name": "April"},
#     {"id": 5, "name": "May"}, {"id": 6, "name": "June"},
#     {"id": 7, "name": "July"}, {"id": 8, "name": "August"},
#     {"id": 9, "name": "September"}, {"id": 10, "name": "October"},
#     {"id": 11, "name": "November"}, {"id": 12, "name": "December"},
# ]

# MONTH_NAME_TO_NUM = {m["name"]: m["id"] for m in MONTHS}
# MONTH_NUM_TO_NAME = {m["id"]: m["name"] for m in MONTHS}








MONTH_NUM_TO_NAME = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

MONTHS = [
    {"id": 1, "name": "January"}, {"id": 2, "name": "February"},
    {"id": 3, "name": "March"}, {"id": 4, "name": "April"},
    {"id": 5, "name": "May"}, {"id": 6, "name": "June"},
    {"id": 7, "name": "July"}, {"id": 8, "name": "August"},
    {"id": 9, "name": "September"}, {"id": 10, "name": "October"},
    {"id": 11, "name": "November"}, {"id": 12, "name": "December"}
]
































# def get_years_list():
#     """Available years for filter dropdown"""
#     from django.utils import timezone
#     current_year = timezone.now().year
  
#     existing_years = list(Payroll.objects.values_list("year", flat=True).distinct())
#     years = sorted(set(existing_years + [current_year, current_year + 1]), reverse=True)
#     return years







# dashboard/views.py

# def get_years_list():
#     """
#     - Past: ALL existing payroll years (records ke saath)
#     - Current: Hamesha rahega
#     - Future: Sirf years, records nahi
#     """
#     from django.utils import timezone
#     from payrolls.models import Payroll
    
#     current_year = timezone.now().year
    
#     # ALL existing payroll years (past + current)
#     # Yeh database mein jo bhi records hain, unke years
#     existing_years = list(
#         Payroll.objects.values_list("year", flat=True).distinct()
#     )
    
#     # Future: next 3 years (sirf years, records nahi)
#     future_years = [current_year + 1, current_year + 2, current_year + 3]
    
#     # Combine and sort (newest first)
#     all_years = sorted(set(existing_years + future_years), reverse=True)
    
#     return all_years


def get_years_list():
    current = timezone.now().year
    return list(range(current - 2, current + 3))








# ─────────────────────────────────────────────────────────────
# PAYROLL LIST VIEW (Main Page)
# ─────────────────────────────────────────────────────────────

# @login_required
# def payroll_list(request):
#     """
#     Main payroll page.
#     - Shows all payroll records
#     - Filters: search, month, year, status
#     - Stats cards: Total, Processed, Pending
#     - Grand Total row
#     - Generate Payroll modal with employee dropdown
#     """
    
#     # ── Get Filter Params ──
#     search_query = request.GET.get("search", "").strip()
#     filter_month = request.GET.get("month", "")
#     filter_year = request.GET.get("year", "")
#     filter_status = request.GET.get("status", "")
    
#     # ── Base Queryset ──
#     payrolls = Payroll.objects.select_related("employee", "employee__designation").all()
    
#     # ── Apply Filters ──
#     if filter_month:
#         month_name = MONTH_NUM_TO_NAME.get(int(filter_month), "")
#         if month_name:
#             payrolls = payrolls.filter(month=month_name)
    
#     if filter_year:
#         payrolls = payrolls.filter(year=int(filter_year))
    
#     if filter_status:
#         payrolls = payrolls.filter(status=filter_status)
    
#     if search_query:
#         payrolls = payrolls.filter(
#             Q(employee__first_name__icontains=search_query) |
#             Q(employee__last_name__icontains=search_query) |
#             Q(employee__employee_code__icontains=search_query)
#         )
    
#     # ── Stats Calculations ──
#     total_payroll = payrolls.aggregate(total=Sum("net_salary"))["total"] or Decimal("0.00")
#     processed_payroll = payrolls.filter(status="paid").aggregate(total=Sum("net_salary"))["total"] or Decimal("0.00")
#     pending_payroll = payrolls.filter(status="pending").aggregate(total=Sum("net_salary"))["total"] or Decimal("0.00")
    
#     # ── Grand Total ──
#     grand_salary = payrolls.aggregate(total=Sum("basic_salary"))["total"] or Decimal("0.00")
#     grand_leave = payrolls.aggregate(total=Sum("leave_deduction"))["total"] or Decimal("0.00")
#     grand_net = payrolls.aggregate(total=Sum("net_salary"))["total"] or Decimal("0.00")
    
#     # ── Employees for Generate Modal ──
#     employees = Employee.objects.filter(employment_status="ACTIVE").select_related("designation")
    
#     context = {
#         # Payroll records
#         "payrolls": payrolls,
        
#         # Filters
#         "months": MONTHS,
#         "years": get_years_list(),
        
#         # Stats
#         "total_payroll": total_payroll,
#         "processed_payroll": processed_payroll,
#         "pending_payroll": pending_payroll,
        
#         # Grand Total
#         "grand_salary": grand_salary,
#         "grand_leave": grand_leave,
#         "grand_net": grand_net,
        
#         # Employees for dropdown
#         "employees": employees,
        
#         # Active filter values (for keeping dropdowns selected)
#         "active_month": filter_month,
#         "active_year": filter_year,
#         "active_status": filter_status,
#         "active_search": search_query,
#     }
    
#     return render(request, "admin/payroll.html", context)
















@login_required
def payroll_list(request):
    """
    Main payroll page.
    - Shows all payroll records
    - Filters: search, month, year, status
    - Stats cards: Total, Processed, Pending
    - Grand Total row
    - Generate Payroll modal with employee dropdown
    """
    
    # ── Get Filter Params ──
    search_query = request.GET.get("search", "").strip()
    filter_month = request.GET.get("month", "")
    filter_year = request.GET.get("year", "")
    filter_status = request.GET.get("status", "")
    
    # ── Base Queryset ──
    payrolls = Payroll.objects.select_related("employee", "employee__designation").all().order_by("-id")
    
    # ── Apply Filters ──
    if filter_month:
        month_name = MONTH_NUM_TO_NAME.get(int(filter_month), "")
        if month_name:
            payrolls = payrolls.filter(month=month_name)
    
    # ✅ YEAR FILTER - Agar select kiya hai toh filter, nahi toh current year
    from django.utils import timezone
    current_year = timezone.now().year
    
    if filter_year:
        payrolls = payrolls.filter(year=int(filter_year))
    else:
        # ✅ Default: Current year ka dikhao (agar koi filter nahi)
        payrolls = payrolls.filter(year=current_year)
        filter_year = str(current_year)  # Dropdown mein select dikhe
    
    if filter_status:
        payrolls = payrolls.filter(status=filter_status)
    
    if search_query:
        payrolls = payrolls.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_code__icontains=search_query)
        )
    
    # ── Stats Calculations ──
    total_payroll = payrolls.aggregate(total=Sum("net_salary"))["total"] or Decimal("0.00")
    processed_payroll = payrolls.filter(status="paid").aggregate(total=Sum("net_salary"))["total"] or Decimal("0.00")
    pending_payroll = payrolls.filter(status="pending").aggregate(total=Sum("net_salary"))["total"] or Decimal("0.00")
    
    # ── Grand Total ──
    grand_salary = payrolls.aggregate(total=Sum("basic_salary"))["total"] or Decimal("0.00")
    grand_leave = payrolls.aggregate(total=Sum("leave_deduction"))["total"] or Decimal("0.00")
    grand_net = payrolls.aggregate(total=Sum("net_salary"))["total"] or Decimal("0.00")
    
    # ── Employees for Generate Modal ──
    employees = Employee.objects.filter(employment_status="ACTIVE").select_related("designation")
    
    context = {
        # Payroll records
        "payrolls": payrolls,
        
        # Filters
        "months": MONTHS,
        "years": get_years_list(),  # ✅ Past + Current + Future
        
        # Stats
        "total_payroll": total_payroll,
        "processed_payroll": processed_payroll,
        "pending_payroll": pending_payroll,
        
        # Grand Total
        "grand_salary": grand_salary,
        "grand_leave": grand_leave,
        "grand_net": grand_net,
        
        # Employees for dropdown
        "employees": employees,
        
        # Active filter values (for keeping dropdowns selected)
        "active_month": filter_month,
        "active_year": filter_year,  # ✅ Current year selected dikhega
        "active_status": filter_status,
        "active_search": search_query,
        "current_year": timezone.now().year,
    }
    
    return render(request, "admin/payroll.html", context)













# ─────────────────────────────────────────────────────────────
# GENERATE PAYROLL (POST)
# ─────────────────────────────────────────────────────────────

# @login_required
# def payroll_generate(request):
#     """
#     Admin generates new payroll record.
#     - Employee select karega
#     - Month & Year select karega
#     - Basic Salary (auto-fill from employee.salary)
#     - Bonus, Leave Deduction, Other Deduction enter karega
#     - Payment Date & Status select karega
#     """
#     if request.method != "POST":
#         return redirect("payroll_list")
    
#     employee_id = request.POST.get("employee_id")
#     month_num = request.POST.get("month")
#     year = request.POST.get("year")
#     basic_salary = request.POST.get("monthly_salary", "0")
#     bonus = request.POST.get("bonus", "0")
#     leave_deduction = request.POST.get("leave_deduction", "0")
#     other_deduction = request.POST.get("other_deduction", "0")
#     payment_date = request.POST.get("payment_date", "")
#     status = request.POST.get("status", "pending")
    
#     # Validation
#     if not all([employee_id, month_num, year]):
#         messages.error(request, "Please select Employee, Month and Year.")
#         return redirect("payroll_list")
    
#     employee = get_object_or_404(Employee, id=employee_id)
#     month_name = MONTH_NUM_TO_NAME.get(int(month_num), "")
    
#     # Check if already exists
#     if Payroll.objects.filter(employee=employee, month=month_name, year=int(year)).exists():
#         messages.error(request, f"Payroll already exists for {employee.full_name} - {month_name} {year}")
#         return redirect("payroll_list")
    
#     # Create Payroll
#     payroll = Payroll.objects.create(
#         employee=employee,
#         month=month_name,
#         year=int(year),
#         basic_salary=Decimal(basic_salary) if basic_salary else employee.salary,
#         bonus=Decimal(bonus) if bonus else Decimal("0.00"),
#         leave_deduction=Decimal(leave_deduction) if leave_deduction else Decimal("0.00"),
#         other_deduction=Decimal(other_deduction) if other_deduction else Decimal("0.00"),
#         payment_date=payment_date if payment_date else None,
#         status=status,
#     )
    
#     messages.success(request, f"Payroll generated for {employee.full_name} - {month_name} {year}")
#     return redirect("dashboard:payroll_list")











from django.db import IntegrityError, transaction
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def payroll_generate(request):
    """
    Admin generates new payroll record.
    - Employee select karega
    - Month & Year select karega
    - Basic Salary (auto-fill from employee.salary)
    - Bonus, Leave Deduction, Other Deduction enter karega
    - Payment Date & Status select karega
    """
    if request.method != "POST":
        return redirect("payroll_list")
    
    # ── Form Data ──
    employee_id = request.POST.get("employee_id")
    month_num = request.POST.get("month")
    year = request.POST.get("year")
    basic_salary = request.POST.get("monthly_salary", "0")
    bonus = request.POST.get("bonus", "0")
    leave_deduction = request.POST.get("leave_deduction", "0")
    other_deduction = request.POST.get("other_deduction", "0")
    payment_date = request.POST.get("payment_date", "")
    status = request.POST.get("status", "pending")
    
    # ── Basic Validation ──
    if not all([employee_id, month_num, year]):
        messages.error(request, "Please select Employee, Month and Year.")
        return redirect("dashboard:payroll_list")
    
    # ── Employee Fetch ──
    employee = get_object_or_404(Employee, id=employee_id)
    month_name = MONTH_NUM_TO_NAME.get(int(month_num), "")
    
    if not month_name:
        messages.error(request, "Invalid month selected.")
        return redirect("dashboard:payroll_list")


     # 🔧 CHANGED: Race condition fix + company details auto-save
    try:
        with transaction.atomic():
            payroll, created = Payroll.objects.get_or_create(
                employee=employee,
                month=month_name,
                year=int(year),
                defaults={
                    "basic_salary": Decimal(basic_salary) if basic_salary else employee.salary,
                    "bonus": Decimal(bonus) if bonus else Decimal("0.00"),
                    "leave_deduction": Decimal(leave_deduction) if leave_deduction else Decimal("0.00"),
                    "other_deduction": Decimal(other_deduction) if other_deduction else Decimal("0.00"),
                    "payment_date": payment_date if payment_date else None,
                    "status": status,
                    
                    # ✅ ADDED: Company details auto-save
                    # "company_ifsc": "UTIB0003146",
                    # "company_reg_no": "U72200MH2021PTC123456",
                    # "company_bank_name": "Axis Bank",
                    # "company_bank_account": "923020058768439",
                }
            )
            if not created:
                messages.error(
                    request,
                    f"Payroll already exists for {employee.full_name} - {month_name} {year}"
                )
                return redirect("dashboard:payroll_list")
    except IntegrityError:
        messages.error(request, "Payroll could not be created due to a conflict. Please try again.")
        return redirect("dashboard:payroll_list")

    messages.success(request, f"Payroll generated for {employee.full_name} - {month_name} {year}")
    return redirect("dashboard:payroll_list")

    









from django.shortcuts import redirect

@login_required
def payroll_delete(request, pk):
    """
    Delete a payroll record.
    - Sirf POST request se delete hoga (security)
    - Delete hone ke baad payroll_list pe redirect
    - Grand Total automatically recalculate hoga (dynamic)
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("dashboard:payroll_list")
    
    payroll = get_object_or_404(Payroll, pk=pk)
    
    emp_name = payroll.employee.full_name
    month_year = f"{payroll.month} {payroll.year}"
    amount = payroll.net_salary
    
    payroll.delete()
    
    messages.success(
        request, 
        f"Payroll deleted for {emp_name} ({month_year}) — ₹{amount}"
    )
    return redirect("dashboard:payroll_list")








    
    # ── Safe Create with Race Condition Fix ──
    # try:
    #     with transaction.atomic():
    #         payroll, created = Payroll.objects.get_or_create(
    #             employee=employee,
    #             month=month_name,
    #             year=int(year),
    #             defaults={
    #                 "basic_salary": Decimal(basic_salary) if basic_salary else employee.salary,
    #                 "bonus": Decimal(bonus) if bonus else Decimal("0.00"),
    #                 "leave_deduction": Decimal(leave_deduction) if leave_deduction else Decimal("0.00"),
    #                 "other_deduction": Decimal(other_deduction) if other_deduction else Decimal("0.00"),
    #                 "payment_date": payment_date if payment_date else None,
    #                 "status": status,
    #             }
    #         )
            
    #         if not created:
    #             # Already exists
    #             messages.error(
    #                 request, 
    #                 f"Payroll already exists for {employee.full_name} - {month_name} {year}"
    #             )
    #             return redirect("dashboard:payroll_list")
                
    # except IntegrityError:
    #     # Database level conflict (edge case)
    #     messages.error(request, "Payroll could not be created due to a conflict. Please try again.")
    #     return redirect("dashboard:payroll_list")
    
    # # ── Success ──
    # messages.success(
    #     request, 
    #     f"Payroll generated for {employee.full_name} - {month_name} {year}"
    # )
    # return redirect("dashboard:payroll_list")











# ─────────────────────────────────────────────────────────────
# PAYROLL DETAIL (View Modal)
# ─────────────────────────────────────────────────────────────

@login_required
def payroll_detail(request, pk):
    """
    Returns JSON for View Modal
    """
    payroll = get_object_or_404(Payroll, pk=pk)
    
    data = {
        "id": payroll.id,
        "employee_id": payroll.employee.id, 
        "employee_name": payroll.employee.full_name,
        "employee_code": payroll.employee.employee_code,
        "designation": payroll.employee.designation.title if payroll.employee.designation else "",
        "month": payroll.month,
        "year": payroll.year,
        "month_year": f"{payroll.month} {payroll.year}",
        "basic_salary": float(payroll.basic_salary),
        "bonus": float(payroll.bonus),
        "leave_deduction": float(payroll.leave_deduction),
        "other_deduction": float(payroll.other_deduction),
        "net_salary": float(payroll.net_salary),
        "payment_date": str(payroll.payment_date) if payroll.payment_date else None,
        "status": payroll.status,
        "annual_ctc": float(payroll.annual_ctc),
        "lpa": payroll.lpa,
        "lpa_display": payroll.lpa_display,
    }
    
    return JsonResponse(data)


# ─────────────────────────────────────────────────────────────
# PAYROLL EDIT (POST)
# ─────────────────────────────────────────────────────────────

@login_required
def payroll_edit(request, pk):
    """
    Admin edits existing payroll
    """
    if request.method != "POST":
        return redirect("payroll_list")
    
    payroll = get_object_or_404(Payroll, pk=pk)
    
    basic_salary = request.POST.get("basic_salary", "0")
    bonus = request.POST.get("bonus", "0")
    leave_deduction = request.POST.get("leave_deduction", "0")
    other_deduction = request.POST.get("other_deduction", "0")
    payment_date = request.POST.get("payment_date", "")
    status = request.POST.get("status", "pending")
    
    payroll.basic_salary = Decimal(basic_salary) if basic_salary else payroll.basic_salary
    payroll.bonus = Decimal(bonus) if bonus else Decimal("0.00")
    payroll.leave_deduction = Decimal(leave_deduction) if leave_deduction else Decimal("0.00")
    payroll.other_deduction = Decimal(other_deduction) if other_deduction else Decimal("0.00")
    payroll.payment_date = payment_date if payment_date else None
    payroll.status = status
    payroll.save()
    
    messages.success(request, "Payroll updated successfully.")
    return redirect("dashboard:payroll_list")


# ─────────────────────────────────────────────────────────────
# MARK AS PAID
# ─────────────────────────────────────────────────────────────

# @login_required
# def payroll_mark_paid(request, pk):
#     """
#     Mark pending/processing payroll as paid
#     """
#     payroll = get_object_or_404(Payroll, pk=pk)
    
#     if payroll.status != "paid":
#         from django.utils import timezone
#         payroll.status = "paid"
#         payroll.payment_date = timezone.now().date()
#         payroll.save()
#         messages.success(request, f"Payroll marked as paid for {payroll.employee.full_name}")
    
#     return redirect("dashboard:payroll_list")






from django.views.decorators.http import require_POST


@login_required
@require_POST  # ✅ GET block ho jayega
def payroll_mark_paid(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    if payroll.status != "paid":
        payroll.status = "paid"
        payroll.payment_date = timezone.now().date()
        payroll.save()
        messages.success(request, f"Payroll marked as paid for {payroll.employee.full_name}")
    return redirect("dashboard:payroll_list")














# @login_required
# def payroll_payment_slip(request, pk):
#     """
#     Payment Slip / Salary Slip as PDF download.
#     Uses WeasyPrint to generate PDF directly from HTML template.
#     """
#     payroll = get_object_or_404(
#         Payroll.objects.select_related("employee", "employee__designation"),
#         pk=pk
#     )

#     # Calculations
#     gross_earnings = Decimal(payroll.basic_salary) + Decimal(payroll.bonus)
#     total_deductions = Decimal(payroll.leave_deduction) + Decimal(payroll.other_deduction)

#     context = {
#         "payroll": payroll,
#         "company_name": "MYCRM Pvt. Ltd.",
#         "company_address": "123 Business Park, Mumbai, Maharashtra - 400001",
#         "company_contact": "info@mycrm.com | +91-9876543210",
#         "gross_earnings": gross_earnings,
#         "total_deductions": total_deductions,
#         "generated_on": timezone.now(),
#     }

#     # HTML template ko string mein render karo
#     html_string = render_to_string("admin/payroll_slip.html", context)

#     # WeasyPrint se PDF generate karo
#     html = HTML(string=html_string, base_url=request.build_absolute_uri())
#     pdf = html.write_pdf()

#     # PDF response banao
#     response = HttpResponse(pdf, content_type="application/pdf")

#     # Filename set karo: Salary_Slip_EMP001_May_2026.pdf
#     filename = f"Salary_Slip_{payroll.employee.employee_code}_{payroll.month}_{payroll.year}.pdf"
#     response["Content-Disposition"] = f'attachment; filename="{filename}"'

#     return response














def amount_in_words(amount):
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def less_than_thousand(num):
        if num == 0:
            return ""
        elif num < 20:
            return ones[num]
        elif num < 100:
            return tens[num // 10] + (" " + ones[num % 10] if num % 10 != 0 else "")
        else:
            return ones[num // 100] + " Hundred" + (" and " + less_than_thousand(num % 100) if num % 100 != 0 else "")

    if amount == 0:
        return "Zero Rupees Only"

    rupees = int(amount)
    paise = int(round((amount - rupees) * 100))

    result = ""
    crore = rupees // 10000000
    lakh = (rupees // 100000) % 100
    thousand = (rupees // 1000) % 100
    hundred = rupees % 1000

    if crore > 0:
        result += less_than_thousand(crore) + " Crore "
    if lakh > 0:
        result += less_than_thousand(lakh) + " Lakh "
    if thousand > 0:
        result += less_than_thousand(thousand) + " Thousand "
    if hundred > 0:
        result += less_than_thousand(hundred)

    result = result.strip() + " Rupees"

    if paise > 0:
        result += " and " + less_than_thousand(paise) + " Paise"

    return result + " Only"


# @login_required
# def payroll_payment_slip(request, pk):


#     payroll = get_object_or_404(
#         Payroll.objects.select_related("employee", "employee__designation"),
#         pk=pk
#     )

#     gross_earnings = Decimal(payroll.basic_salary) + Decimal(payroll.bonus)
#     total_deductions = Decimal(payroll.leave_deduction) + Decimal(payroll.other_deduction)

#     # ✅ SIGNATURE IMAGE KA URL BANAO
#     sign_url = request.build_absolute_uri(static("images/authorized_sign.png"))

#     context = {
#         "payroll": payroll,
#         "company_name": "Prestigieux Mediatech Pvt. Ltd.",
#         "company_address": "123 Business Park, Mumbai, Maharashtra - 400001",
#         "company_contact": "info@mycrm.com | +91-9876543210",
#         "gross_earnings": gross_earnings,
#         "total_deductions": total_deductions,
#         "net_in_words": amount_in_words(float(payroll.net_salary)),
#         "generated_on": timezone.now(),
#         "sign_url": sign_url, 
#     }

#     html_string = render_to_string("admin/payroll_slip.html", context)
#     html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
#     pdf = html.write_pdf()

#     response = HttpResponse(pdf, content_type="application/pdf")
#     filename = f"Salary_Slip_{payroll.employee.employee_code}_{payroll.month}_{payroll.year}.pdf"
#     response["Content-Disposition"] = f'attachment; filename="{filename}"'
#     return response








@login_required
def payroll_payment_slip(request, pk):
    try:
        payroll = get_object_or_404(
            Payroll.objects.select_related("employee", "employee__designation"),
            pk=pk
        )

        gross_earnings = Decimal(payroll.basic_salary) + Decimal(payroll.bonus)
        total_deductions = Decimal(payroll.leave_deduction) + Decimal(payroll.other_deduction)

        sign_url = request.build_absolute_uri(static("images/authorized_sign.png"))

        context = {
            "payroll": payroll,
            
            # ✅ ADDED: Employee bank details from Employee model
            "emp_bank_name": payroll.employee.bank_name or "-",
            "emp_account": payroll.employee.bank_account or "-",

             # ✅ Company details — hardcoded (model se mat lo)
            "company_name": "PRESTIGIEUX MEDIATECH PVT LTD", 
            "company_reg_no": "U62099MH2023PTC410296",
            "company_bank_name": "Axis Bank",
            "company_bank_account": "923020058768439",
            "company_ifsc": "UTIB0003146",



                    # ✅ Fallback — agar payroll record purana hai (empty fields)
            # "company_gst": payroll.company_gst or "27AAJCP1234F1Z5",
            # "company_reg_no": payroll.company_reg_no or "U72200MH2021PTC123456",
            # "company_bank_name": payroll.company_bank_name or "Axis Bank",
            # "company_bank_account": payroll.company_bank_account or "923020058768439",
            # "company_ifsc": "UTIB0003146",  # static




            "gross_earnings": gross_earnings,
            "total_deductions": total_deductions,
            "net_in_words": amount_in_words(float(payroll.net_salary)),
            "generated_on": timezone.now(),
            "sign_url": sign_url,
        }

        html_string = render_to_string("admin/payroll_slip.html", context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        filename = f"Salary_Slip_{payroll.employee.employee_code}_{payroll.month}_{payroll.year}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        # logger.error(f"PDF generation failed: {str(e)}")
        messages.error(request, "Failed to generate payment slip. Please try again.")
        return redirect("dashboard:payroll_list")




































































# ─────────────────────────────────────────────────────────────
# ANNUAL BREAKDOWN (View Annual Breakdown Modal)
# ─────────────────────────────────────────────────────────────

@login_required
def payroll_annual_breakdown(request, employee_id, year):
    """
    Returns JSON for Annual Breakdown Modal
    - 12 months ka data
    - Total Paid, Total Pending, Total Deductions
    - Grand totals
    """
    employee = get_object_or_404(Employee, pk=employee_id)
    
    # Get all payrolls for this employee in this year
    payrolls = Payroll.objects.filter(employee=employee, year=int(year)).order_by("month")
    
    # Create month-wise map
    payroll_map = {}
    for p in payrolls:
        payroll_map[p.month] = p
    
    # Build 12 months data
    months_data = []
    total_paid = Decimal("0.00")
    total_pending = Decimal("0.00")
    total_deductions = Decimal("0.00")
    
    grand_base = Decimal("0.00")
    grand_leave = Decimal("0.00")
    grand_net = Decimal("0.00")
    
    for m in MONTHS:
        month_name = m["name"]
        if month_name in payroll_map:
            p = payroll_map[month_name]
            deductions = p.leave_deduction + p.other_deduction
            
            if p.status == "paid":
                total_paid += p.net_salary
            else:
                total_pending += p.net_salary
            
            total_deductions += deductions
            grand_base += p.basic_salary
            grand_leave += p.leave_deduction
            grand_net += p.net_salary
            
            months_data.append({
                "month": month_name,
                "base_salary": float(p.basic_salary),
                "leave_deduction": float(p.leave_deduction),
                "net_salary": float(p.net_salary),
                "payment_date": str(p.payment_date) if p.payment_date else None,
                "status": p.status,
                "generated": True,
            })
        else:
            months_data.append({
                "month": month_name,
                "base_salary": None,
                "leave_deduction": None,
                "net_salary": None,
                "payment_date": None,
                "status": "not_generated",
                "generated": False,
            })
    
    data = {
        "employee": {
            "id": employee.id,
            "name": employee.full_name,
            "code": employee.employee_code,
            "designation": employee.designation.title if employee.designation else "",
            "annual_ctc": float(employee.salary * 12),
            "lpa": float(employee.salary * 12) / 100000,
            "lpa_display": f"{float(employee.salary * 12) / 100000:.2f} LPA",
        },
        "year": int(year),
        "months": months_data,
        "summary": {
            "total_paid": float(total_paid),
            "total_pending": float(total_pending),
            "total_deductions": float(total_deductions),
        },
        "grand_totals": {
            "base_salary": float(grand_base),
            "leave_deduction": float(grand_leave),
            "net_salary": float(grand_net),
        },
    }
    
    return JsonResponse(data)


# ─────────────────────────────────────────────────────────────
# GET EMPLOYEE SALARY (AJAX for auto-fill in Generate Modal)
# ─────────────────────────────────────────────────────────────

@login_required
def get_employee_salary(request):
    """
    AJAX endpoint to get employee's default salary
    """
    employee_id = request.GET.get("employee_id")
    if not employee_id:
        return JsonResponse({"error": "No employee_id provided"}, status=400)
    
    try:
        employee = Employee.objects.get(pk=employee_id)
        return JsonResponse({
            "salary": float(employee.salary),
            "name": employee.full_name,
            "code": employee.employee_code,
        })
    except Employee.DoesNotExist:
        return JsonResponse({"error": "Employee not found"}, status=404)









# def leave_requests(request):
#     return render(request, "admin/leave.html")


# @login_required
# @user_passes_test(is_admin)
# def leave_requests(request):
#     status_filter = request.GET.get("status", "All")
    
#     leaves = Leave.objects.select_related("employee", "reviewed_by").all()
    
#     if status_filter != "All":
#         leaves = leaves.filter(status=status_filter.lower())
    
#     leaves_data = []
#     for leave in leaves:
#         leaves_data.append({
#             "id": leave.id,
#             "employee": {
#                 "id": leave.employee.id,
#                 "first_name": leave.employee.first_name,
#                 "last_name": leave.employee.last_name,
#             },
#             "leave_type": leave.leave_type,
#             "start_date": leave.start_date.isoformat() if leave.start_date else None,
#             "end_date": leave.end_date.isoformat() if leave.end_date else None,
#             "reason": leave.reason,
#             "status": leave.status,
#             "reviewed_by": leave.reviewed_by.get_full_name() if leave.reviewed_by else None,
#             "reviewed_at": leave.reviewed_at.isoformat() if leave.reviewed_at else None,
#         })
    
#     context = {
#         "current_date": timezone.now().strftime("%d %b %Y"),
#         "leaves_json": json.dumps(leaves_data, cls=DjangoJSONEncoder),
#         "status_filter": status_filter,
#     }
#     return render(request, "admin/leave.html", context)


# @login_required
# @user_passes_test(is_admin)
# @require_POST
# def update_leave_status(request):
#     try:
#         data = json.loads(request.body)
#         leave_id = data.get("leave_id")
#         status = data.get("status")
        
#         if status not in ["approved", "rejected"]:
#             return JsonResponse({
#                 "success": False,
#                 "error": "Invalid status"
#             }, status=400)
        
#         leave = get_object_or_404(Leave, id=leave_id)
        
#         leave.status = status
#         leave.reviewed_by = request.user
#         leave.reviewed_at = timezone.now()
#         leave.save()
        
#         return JsonResponse({
#             "success": True,
#             "message": f"Leave {status} successfully",
#             "leave": {
#                 "id": leave.id,
#                 "status": leave.status,
#                 "reviewed_by": request.user.get_full_name() or request.user.username,
#                 "reviewed_at": leave.reviewed_at.isoformat(),
#             }
#         })
        
#     except json.JSONDecodeError:
#         return JsonResponse({
#             "success": False,
#             "error": "Invalid JSON"
#         }, status=400)
#     except Exception as e:
#         return JsonResponse({
#             "success": False,
#             "error": str(e)
#         }, status=500)









# @login_required
# @user_passes_test(is_admin)
# def leave_requests(request):
#     status_filter = request.GET.get("status", "All")
    
#     leaves = Leave.objects.select_related("employee", "reviewed_by").all()
    
#     if status_filter != "All":
#         leaves = leaves.filter(status=status_filter.lower())
    
#     leaves_data = []
#     for leave in leaves:
#         # reviewed_by ka full name nikaalo — get_full_name() ki jagah manual
#         reviewed_by_name = None
#         if leave.reviewed_by:
#             # Pehle first_name + last_name try karo
#             if hasattr(leave.reviewed_by, 'first_name') and leave.reviewed_by.first_name:
#                 reviewed_by_name = f"{leave.reviewed_by.first_name} {leave.reviewed_by.last_name or ''}".strip()
#             else:
#                 # Nahi toh username
#                 reviewed_by_name = getattr(leave.reviewed_by, 'username', 'Admin')
        
#         leaves_data.append({
#             "id": leave.id,
#             "employee": {
#                 "id": leave.employee.id,
#                 "first_name": leave.employee.first_name,
#                 "last_name": leave.employee.last_name,
#             },
#             "leave_type": leave.leave_type,
#             "start_date": leave.start_date.isoformat() if leave.start_date else None,
#             "end_date": leave.end_date.isoformat() if leave.end_date else None,
#             "reason": leave.reason,
#             "status": leave.status,
#             "reviewed_by": reviewed_by_name,
#             "reviewed_at": leave.reviewed_at.isoformat() if leave.reviewed_at else None,
#         })
    
#     context = {
#         "current_date": timezone.now().strftime("%d %b %Y"),
#         "leaves_json": json.dumps(leaves_data, cls=DjangoJSONEncoder),
#         "status_filter": status_filter,
#     }
#     return render(request, "admin/leave.html", context)







from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.views.decorators.http import require_POST
import json

from report.models import Leave


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def leave_requests(request):
    status_filter = request.GET.get("status", "All")
    
    leaves = Leave.objects.select_related("employee", "reviewed_by").all().order_by("-id")
    
    if status_filter != "All":
        leaves = leaves.filter(status=status_filter.lower())
    
    leaves_data = []
    for leave in leaves:
        reviewed_by_name = None
        if leave.reviewed_by:
            if hasattr(leave.reviewed_by, 'first_name') and leave.reviewed_by.first_name:
                reviewed_by_name = f"{leave.reviewed_by.first_name} {leave.reviewed_by.last_name or ''}".strip()
            else:
                reviewed_by_name = getattr(leave.reviewed_by, 'username', 'Admin')
        
        leaves_data.append({
            "id": leave.id,
            "employee": {
                "id": leave.employee.id if leave.employee else None,
                "first_name": leave.employee.first_name if leave.employee else "",
                "last_name": leave.employee.last_name if leave.employee else "",
            } if leave.employee else None,
            "leave_type": leave.leave_type,
            "start_date": leave.start_date.isoformat() if leave.start_date else None,
            "end_date": leave.end_date.isoformat() if leave.end_date else None,
            "reason": leave.reason,
            "status": leave.status,
            "reviewed_by": reviewed_by_name,
            "reviewed_at": leave.reviewed_at.isoformat() if leave.reviewed_at else None,
        })
    
    context = {
        "current_date": timezone.now().strftime("%d %b %Y"),
        "leaves_data": leaves_data,  # <-- Direct list pass karo, json.dumps mat karo
        "status_filter": status_filter,
    }
    return render(request, "admin/leave.html", context)






















from report.services import approve_leave, reject_leave



@login_required
@user_passes_test(is_admin)
@require_POST
def update_leave_status(request):
    try:
        data = json.loads(request.body)
        leave_id = data.get("leave_id")
        status = data.get("status")

        
        if status not in ["approved", "rejected"]:
            return JsonResponse({
                "success": False,
                "error": "Invalid status"
            }, status=400)
        
        leave = get_object_or_404(Leave, id=leave_id)
        
        # leave.status = status
        # leave.reviewed_by = request.user
        # leave.reviewed_at = timezone.now()
        # leave.save()



                # ✅✅✅ YEH 4 LINES HATA KE YEH LAGA ✅✅✅
        if status == "approved":
            approve_leave(leave, request.user)   # ← Attendance bhi banega
        else:
            reject_leave(leave, request.user)    # ← Sirf reject hoga




        
        # reviewed_by name nikaalo — get_full_name() ki jagah manual
        reviewed_by_name = "Admin"
        if hasattr(request.user, 'first_name') and request.user.first_name:
            reviewed_by_name = f"{request.user.first_name} {request.user.last_name or ''}".strip()
        elif hasattr(request.user, 'username'):
            reviewed_by_name = request.user.username
        
        return JsonResponse({
            "success": True,
            "message": f"Leave {status} successfully",
            "leave": {
                "id": leave.id,
                "status": leave.status,
                "reviewed_by": reviewed_by_name,
                "reviewed_at": leave.reviewed_at.isoformat(),
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)







# New updated kimi code upar wala coment hai original code hai upar wala 







from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(is_admin)
def report_list(request):
    # 1. Search Query aur Date Read Karo
    search_query = request.GET.get("q", "").strip()
    date_str = request.GET.get("date")

    # 2. Selected Date Parsing
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    current_year = timezone.now().year
    reports_queryset = Report.objects.select_related("employee")

    # 3. Filtering Logic
    if search_query:
        # NAAM SEARCH KIYA: Employee ki CURRENT YEAR ki SAARI reports aayengi
        reports = (
            reports_queryset.filter(
                Q(employee__first_name__icontains=search_query) |
                Q(employee__last_name__icontains=search_query),
                report_date__year=current_year
            )
            .order_by("-report_date", "-submitted_at")
        )
    else:
        # SEARCH KHALI HAI: Sirf Selected Date ki reports aayengi
        reports = (
            reports_queryset.filter(report_date=selected_date)
            .order_by("-submitted_at")
        )

    # 4. Data Conversion for JS
    reports_data = []
    for report in reports:
        reports_data.append({
            "id": report.id,
            "employee": {
                "id": report.employee.id,
                "first_name": report.employee.first_name,
                "last_name": report.employee.last_name,
            },
            "subject": report.subject,
            "work_summary": report.work_summary,
            "report_date": report.report_date.isoformat() if report.report_date else None,
            "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
            "updated_at": report.updated_at.isoformat() if report.updated_at else None,
            "attachment": report.attachment.url if report.attachment else None,
        })

    context = {
        "current_date": timezone.now().strftime("%d %b %Y"),
        "selected_date": selected_date.strftime("%Y-%m-%d"),
        "selected_date_display": selected_date.strftime("%d %b %Y"),
        "search_query": search_query,
        "reports_data": reports_data,
    }
    return render(request, "admin/report.html", context)




























































































# def report_list(request):
#     return render(request, "admin/report.html")






# @login_required
# @user_passes_test(is_admin)
# def report_list(request):


#     # Search query fetch karo
#     search_query = request.GET.get("q", "").strip()



#       # ── Date Filter ───────────────────────────────────────────
#     # URL se date aaya toh use karo, nahi toh aaj ki date
#     date_str = request.GET.get("date")
#     if date_str:
#         try:
#             selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#         except ValueError:
#             selected_date = timezone.now().date()
#     else:
#         selected_date = timezone.now().date()


#     current_year = timezone.now().year
#     reports_queryset = Report.objects.select_related("employee")


#     if search_query:
#         reports = (
#             reports_queryset.filter(
#                 Q(employee__first_name__icontains=search_query) |
#                 Q(employee__last_name__icontains=search_query),
#                 report_date__year=current_year
#             )
#             .order_by("-submitted_at")
#         )



#     else:
#         # Default: Selected date ki reports
#         reports = (
#             reports_queryset.filter(report_date=selected_date)
#             .order_by("-submitted_at")
#         )

#           # ── Fetch Reports (Sirf selected date ki) ─────────────────
#     # reports = (
#     #     Report.objects
#     #     .select_related("employee")
#     #     .filter(report_date=selected_date)  # <-- YEH ADD KAR
#     #     .order_by("-submitted_at")
#     # )
  

#     # reports = Report.objects.select_related("employee").all().order_by("-report_date", "-submitted_at")



    
#     reports_data = []
#     for report in reports:
#         reports_data.append({
#             "id": report.id,
#             "employee": {
#                 "id": report.employee.id,
#                 "first_name": report.employee.first_name,
#                 "last_name": report.employee.last_name,
#             },
#             "subject": report.subject,
#             "work_summary": report.work_summary,
#             "report_date": report.report_date.isoformat() if report.report_date else None,
#             "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
#             "updated_at": report.updated_at.isoformat() if report.updated_at else None,
#             "attachment": report.attachment.url if report.attachment else None,
#         })
    
#     context = {
#         "current_date": timezone.now().strftime("%d %b %Y"),
#         "selected_date": selected_date.strftime("%Y-%m-%d"),
#         "selected_date_display": selected_date.strftime("%d %b %Y"),
#         "search_query": search_query,
#         "reports_data": reports_data,
       
#     }
#     return render(request, "admin/report.html", context)


# ═══════════════════════════════════════════════════════════════
# EMPLOYEE REPORT VIEWS
# ═══════════════════════════════════════════════════════════════

from django.core.paginator import Paginator

def is_admin(user):
    return user.is_staff or user.is_superuser


def is_employee(user):
    return hasattr(user, "employee_profile")



from django.core.exceptions import ValidationError


# @login_required
# @user_passes_test(is_employee)
# def employee_report_submit(request):
#     employee = request.user.employee_profile
    
#     if request.method == "POST":
#         subject = request.POST.get("subject", "").strip()
#         work_summary = request.POST.get("work_summary", "").strip()
#         report_date = request.POST.get("report_date", "").strip()
        
#         errors = {}
#         if not subject:
#             errors["subject"] = "Subject is required"
#         elif len(subject) < 3:
#             errors["subject"] = "Subject must be at least 3 characters"
            
#         if not work_summary:
#             errors["work_summary"] = "Work summary is required"
#         elif len(work_summary) < 10:
#             errors["work_summary"] = "Work summary must be at least 10 characters"
            
#         if not report_date:
#             errors["report_date"] = "Report date is required"


#         if errors:
#             if request.headers.get("X-Requested-With") == "XMLHttpRequest":
#                 return JsonResponse({"success": False, "errors": errors}, status=400)
            
#             context = {
#                 "errors": errors,
#                 "form_data": {
#                     "subject": subject,
#                     "work_summary": work_summary,
#                     "report_date": report_date,
#                 },
#             }
#             return render(request, "employee/report_submit.html", context)
        
#         try:
#             report = Report.objects.create(
#                 employee=employee,
#                 subject=subject,
#                 work_summary=work_summary,
#                 report_date=report_date,
#             )
            
#             if request.FILES.get("attachment"):
#                 report.attachment = request.FILES["attachment"]
#                 report.save()
            
#             if request.headers.get("X-Requested-With") == "XMLHttpRequest":
#                 return JsonResponse({
#                     "success": True,
#                     "message": "Report submitted successfully!",
#                     "report": {
#                         "id": report.id,
#                         "subject": report.subject,
#                         "report_date": report.report_date.strftime("%d %b %Y"),
#                     }
#                 })
            
#             return redirect("employee_report_history")
            
#         except Exception as e:
#             if request.headers.get("X-Requested-With") == "XMLHttpRequest":
#                 return JsonResponse({"success": False, "error": str(e)}, status=500)
#             raise
    
#     context = {
#         "errors": {},
#         "form_data": {},
#         "today": timezone.now().date().isoformat(),
#     }
#     return render(request, "employee/report_submit.html", context)









from django.core.exceptions import ValidationError

@login_required
@user_passes_test(is_employee)
def employee_report_submit(request):
    employee = request.user.employee_profile
    
    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        work_summary = request.POST.get("work_summary", "").strip()
        report_date = request.POST.get("report_date", "").strip()
        
        errors = {}
        if not subject:
            errors["subject"] = "Subject is required"
        elif len(subject) < 3:
            errors["subject"] = "Subject must be at least 3 characters"
            
        if not work_summary:
            errors["work_summary"] = "Work summary is required"
        elif len(work_summary) < 10:
            errors["work_summary"] = "Work summary must be at least 10 characters"
            
        if not report_date:
            errors["report_date"] = "Report date is required"
        
        # 🟢 IMAGE SIZE CHECK — before saving
        attachment = request.FILES.get("attachment")
        if attachment:
            if attachment.size > 5 * 1024 * 1024:
                errors["attachment"] = "Image size must be under 5MB"
        
        if errors:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": errors}, status=400)
            context = {
                "errors": errors,
                "form_data": {
                    "subject": subject,
                    "work_summary": work_summary,
                    "report_date": report_date,
                },
            }
            return render(request, "employee/report_submit.html", context)
        
        # 🟢 SAVE WITH TRANSACTION
        from django.db import transaction, IntegrityError
        try:
            with transaction.atomic():
                report = Report.objects.create(
                    employee=employee,
                    subject=subject,
                    work_summary=work_summary,
                    report_date=report_date,
                )
                
                if attachment:
                    report.attachment = attachment
                    report.save()   # 🟢 Yahan model validator chalega (size check)
                    
        except IntegrityError:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": False, 
                    "error": "You have already submitted a report for this date."
                }, status=400)
            context = {"errors": {"general": "You have already submitted a report for this date."}}
            return render(request, "employee/report_submit.html", context)
            
        except ValidationError as e:   # 🟢 NAYA: Model validator se aaya error
            error_msg = " ".join(e.messages) if hasattr(e, 'messages') else str(e)
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "error": error_msg}, status=400)
            context = {"errors": {"attachment": error_msg}}
            return render(request, "employee/report_submit.html", context)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Report submission failed: {str(e)}")
            
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": False, 
                    "error": "Failed to save report. Please try again."
                }, status=500)
            raise
        
        # Success
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "message": "Report submitted successfully!",
                "report": {
                    "id": report.id,
                    "subject": report.subject,
                    "report_date": report.report_date.strftime("%d %b %Y"),
                }
            })
        
        return redirect("employee_report_history")
    
    # GET
    context = {
        "errors": {},
        "form_data": {},
        "today": timezone.now().date().isoformat(),
    }
    return render(request, "employee/report_submit.html", context)






























@login_required
@user_passes_test(is_employee)
def employee_report_history(request):
    employee = request.user.employee_profile
    reports = Report.objects.filter(employee=employee).order_by("-report_date", "-submitted_at")
    
    context = {
        "reports": reports,
        "employee": employee,
    }
    return render(request, "employee/report_history.html", context)

