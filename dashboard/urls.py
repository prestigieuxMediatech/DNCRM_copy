from django.urls import path
from django.views.generic import RedirectView

from .views import (
    send_whatsapp_api,
    admin_approve_leave,
    admin_dashboard,
    user_list,
    user_api,         
    user_detail_api,    
    employee_list,
    add_employee,
    edit_employee,
    view_employee,
    delete_employee,
    department_list,
    add_department,
    edit_department,
    delete_department,
    designation_list,
    add_designation,
    edit_designation,
    delete_designation,
    attendance_list,
    employee_attendance_calendar,
    punch_sessions,
    PunchSessionListAPIView,
    project_list,
    ProjectListCreateAPIView,
    ProjectRetrieveUpdateDestroyAPIView,
    ClientListAPIView,
    EmployeeListAPIView,
    UserListAPIView,
    client_list,
    client_get_all,
    client_create,
    client_get_one,
    client_update,
    client_delete,

    service_list,
    service_get_all,
    service_create,
    service_get_one,
    service_update,
    service_delete,


    invoice_list,
    invoice_get_all,
    invoice_create,
    invoice_get_one,
    invoice_update,
    invoice_delete,
    invoice_pdf_view,



    invoice_item_list,
    invoice_item_get_all,
    invoice_item_create,
    invoice_item_get_one,
    invoice_item_update,
    invoice_item_delete,





    payroll_list,
    payroll_generate,
    payroll_detail,
    payroll_edit,
    payroll_mark_paid,
    payroll_payment_slip,
    payroll_delete,
    payroll_annual_breakdown,
    get_employee_salary,
   




    leave_requests,
    update_leave_status,
    report_list,
    employee_report_submit,
    employee_report_history,
    

 
   
    admin_reject_leave,
    employee_attendance,
    employee_dashboard,
    employee_profile,
    employee_projects,
    # employee_punch_in,
    employee_punchin,
    employee_punch_out,
    employee_reports,
)

app_name = "dashboard"

urlpatterns = [

    path('send-whatsapp-api/', send_whatsapp_api, name='send_whatsapp_api'),

    path("admin/", admin_dashboard, name="admin_dashboard"),
    path("admin/users/", user_list, name="user_list"),
    path("admin/users/api/", user_api, name="user_api"),                          # ← ADD
    path("admin/users/api/<int:user_id>/", user_detail_api, name="user_detail_api"),  # ← ADD

    path("admin/employees/", employee_list, name="employee_list"),
    path("admin/employees/add/", add_employee, name="add_employee"),
    path("admin/employees/<int:pk>/edit/", edit_employee, name="edit_employee"),
    path("admin/employees/<int:pk>/view/", view_employee, name="view_employee"),
    path("admin/employees/<int:pk>/delete/", delete_employee, name="delete_employee"),


    path("admin/departments/", department_list, name="department_list"),
    path("admin/departments/add/", add_department, name="add_department"),
    path("admin/departments/<int:pk>/edit/", edit_department, name="edit_department"),
    path("admin/departments/<int:pk>/delete/", delete_department, name="delete_department"),

    path("admin/designations/", designation_list, name="designation_list"),
    path("admin/designations/add/", add_designation, name="add_designation"),
    path("admin/designations/<int:pk>/edit/", edit_designation, name="edit_designation"),
    path("admin/designations/<int:pk>/delete/", delete_designation, name="delete_designation"),

    path("admin/attendance/", attendance_list, name="attendance_list"),
    path(
        "admin/attendance/api/calendar/<int:employee_id>/", 
        employee_attendance_calendar, 
        name="employee_attendance_calendar"
    ),
    # path("admin/attendance/api/calendar/<int:employee_id>/", 
    #  employee_attendance_calendar, 
    #  name="employee_attendance_calendar"),

path("admin/punch-sessions/", punch_sessions, name="punch_sessions"),
   path("api/punch-sessions/", PunchSessionListAPIView.as_view(), name="punch_sessions_api"),



path("admin/projects/", project_list, name="project_list"),
path("api/projects/", ProjectListCreateAPIView.as_view(), name="project_list_api"),
path("api/projects/<int:pk>/", ProjectRetrieveUpdateDestroyAPIView.as_view(), name="project_detail_api"),
path("api/clients/", ClientListAPIView.as_view(), name="client_list_api"),
path("api/employees/", EmployeeListAPIView.as_view(), name="employee_list_api"),
path("api/users/", UserListAPIView.as_view(), name="user_list_api"),

path("admin/clients/", client_list, name="client_list"),

  # API endpoints — har action ke liye alag
path("api/clients/create/", client_create, name="client_create"),      # CREATE
path("api/clients/", client_get_all, name="client_get_all"),           # LIST
path("api/clients/<int:pk>/", client_get_one, name="client_get_one"),   # GET ONE
path("api/clients/<int:pk>/update/", client_update, name="client_update"),  # UPDATE
path("api/clients/<int:pk>/delete/", client_delete, name="client_delete"),   # DELETE





    # ─── NEW: Services ───
    path("admin/services/", service_list, name="service_list"),
    path("api/services/", service_get_all, name="service_get_all"),
    path("api/services/create/", service_create, name="service_create"),
    path("api/services/<int:pk>/", service_get_one, name="service_get_one"),
    path("api/services/<int:pk>/update/", service_update, name="service_update"),
    path("api/services/<int:pk>/delete/", service_delete, name="service_delete"),

    # ─── NEW: Invoices ───
    path("admin/invoices/", invoice_list, name="invoice_list"),
    path("api/invoices/", invoice_get_all, name="invoice_get_all"),
    path("api/invoices/create/", invoice_create, name="invoice_create"),
    path("api/invoices/<int:pk>/", invoice_get_one, name="invoice_get_one"),
    path("api/invoices/<int:pk>/update/", invoice_update, name="invoice_update"),
    path("api/invoices/<int:pk>/delete/", invoice_delete, name="invoice_delete"),
    path("api/invoices/<int:pk>/pdf/", invoice_pdf_view, name="invoice_pdf"),

    # ─── NEW: Invoice Items ───
    path("admin/invoice-items/", invoice_item_list, name="invoice_item_list"),
    path("api/invoices/<int:invoice_id>/items/", invoice_item_get_all, name="invoice_item_get_all"),
    path("api/invoice-items/create/", invoice_item_create, name="invoice_item_create"),
    # path("api/invoices/<int:invoice_id>/items/create/", invoice_item_create, name="invoice_item_create"),
    path("api/invoice-items/<int:pk>/", invoice_item_get_one, name="invoice_item_get_one"),
    path("api/invoice-items/<int:pk>/update/", invoice_item_update, name="invoice_item_update"),
    path("api/invoice-items/<int:pk>/delete/", invoice_item_delete, name="invoice_item_delete"),












path("admin/payroll/", payroll_list, name="payroll_list"),
path("admin/payroll/generate/", payroll_generate, name="payroll_generate"),
path("admin/payroll/<int:pk>/detail/", payroll_detail, name="payroll_detail"),
path("admin/payroll/<int:pk>/edit/", payroll_edit, name="payroll_edit"),
path("admin/payroll/<int:pk>/mark-paid/", payroll_mark_paid, name="payroll_mark_paid"),
path("admin/payroll/<int:pk>/payment-slip/", payroll_payment_slip, name="payroll_payment_slip"),
path("admin/payroll/<int:pk>/delete/", payroll_delete, name="payroll_delete"),
path("admin/payroll/annual/<int:employee_id>/<int:year>/", payroll_annual_breakdown, name="payroll_annual_breakdown"),
path("admin/payroll/ajax/employee-salary/", get_employee_salary, name="get_employee_salary"),





path("admin/leave-requests/", leave_requests, name="leave_requests"),
path("api/leave/update-status/", update_leave_status, name="update_leave_status"),

path("admin/reports/", report_list, name="report_list"),
  # Employee Reports
path("employee/reports/submit/", employee_report_submit, name="employee_report_submit"),
path("employee/reports/history/", employee_report_history, name="employee_report_history"),


path(
        "admin/leaves/<int:leave_id>/approve/",
        admin_approve_leave,
        name="admin_approve_leave",
    ),
path(
        "admin/leaves/<int:leave_id>/reject/",
        admin_reject_leave,
        name="admin_reject_leave",
    ),












    # path(
    #     "admin/employees/",
    #     RedirectView.as_view(pattern_name="dashboard:admin_dashboard", permanent=False),
    #     name="employee_management",
    # ),
    # path(
    #     "admin/departments/",
    #     RedirectView.as_view(pattern_name="dashboard:admin_dashboard", permanent=False),
    #     name="department_management",
    # ),
    # path(
    #     "admin/designations/",
    #     RedirectView.as_view(pattern_name="dashboard:admin_dashboard", permanent=False),
    #     name="designation_management",
    # ),
    # path(
    #     "admin/projects/",
    #     RedirectView.as_view(pattern_name="dashboard:admin_dashboard", permanent=False),
    #     name="admin_projects",
    # ),
    # path(
    #     "admin/attendance/",
    #     RedirectView.as_view(pattern_name="dashboard:admin_dashboard", permanent=False),
    #     name="admin_attendance",
    # ),
    # path(
    #     "admin/reports/",
    #     RedirectView.as_view(pattern_name="dashboard:admin_dashboard", permanent=False),
    #     name="admin_reports",
    # ),



path("employee/", employee_dashboard, name="employee_dashboard"),
    # path("employee/punch-in/", employee_punch_in, name="employee_punch_in"),
path("employee/punch-out/", employee_punch_out, name="employee_punch_out"),
path(
        "employee/profile/",
        employee_profile,
        name="employee_profile",
    ),
path(
        "employee/projects/",
        employee_projects,
        name="employee_projects",
    ),
path(
        "employee/reports/",
        employee_reports,
        name="employee_reports",
    ),
path(
        "employee/attendance/",
        employee_attendance,
        name="employee_attendance",
    ),
path(
        "employee/punchin/",
        employee_punchin,
        name="employee_punchin",
    ),
]
