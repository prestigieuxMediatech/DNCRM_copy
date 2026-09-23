from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

from Punch.models import PunchSession


class PunchSessionSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    emp_code = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()
    
    # EXPLICIT fields add karo
    punch_in_date = serializers.SerializerMethodField()
    punch_in_time = serializers.SerializerMethodField()
    punch_out_date = serializers.SerializerMethodField()
    punch_out_time = serializers.SerializerMethodField()
    
    total_hours = serializers.SerializerMethodField()
    total_minutes = serializers.SerializerMethodField()

    class Meta:
        model = PunchSession
        fields = [
            "id",
            "employee",
            "emp_code",
            "department",
            "attendance",
            "date",
            "punch_in_at",
            "punch_out_at",
            "punch_in_date",
            "punch_in_time",
            "punch_out_date",
            "punch_out_time",
            "total_hours",
            "total_minutes",
            "status",
        ]

    def get_employee(self, obj):
        if obj.employee:
            return getattr(obj.employee, 'full_name', str(obj.employee))
        return "—"

    def get_emp_code(self, obj):
        if obj.employee:
            return getattr(obj.employee, 'employee_code', "—")
        return "—"

    def get_department(self, obj):
        if obj.employee and hasattr(obj.employee, 'department'):
            dept = obj.employee.department
            if dept:
                return getattr(dept, 'name', str(dept))
        return "—"

    def get_attendance(self, obj):
        if obj.attendance:
            return obj.attendance.get_status_display()
        return "—"

    # ========== EXPLICIT TIME/DATE METHODS ==========
    def get_punch_in_date(self, obj):
        if obj.punch_in_at:
            return timezone.localtime(obj.punch_in_at).strftime('%Y-%m-%d')
        return None

    def get_punch_in_time(self, obj):
        if obj.punch_in_at:
            return timezone.localtime(obj.punch_in_at).strftime('%I:%M %p')  # "10:27 AM"
        return None

    def get_punch_out_date(self, obj):
        if obj.punch_out_at:
            return timezone.localtime(obj.punch_out_at).strftime('%Y-%m-%d')
        return None

    def get_punch_out_time(self, obj):
        if obj.punch_out_at:
            return timezone.localtime(obj.punch_out_at).strftime('%I:%M %p')  # "05:11 PM"
        return None

    # ========== TOTAL HOURS ==========
    def get_total_hours(self, obj):
        punch_in = obj.punch_in_at
        punch_out = obj.punch_out_at
        
        if not punch_in:
            return Decimal("0.00")
        
        if not punch_out:
            punch_out = timezone.now()
        
        duration = punch_out - punch_in
        total_seconds = max(duration.total_seconds(), 0)
        hours = Decimal(total_seconds) / Decimal(3600)
        hours = hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return hours

    def get_total_minutes(self, obj):
        punch_in = obj.punch_in_at
        punch_out = obj.punch_out_at
        
        if not punch_in:
            return 0
        
        if not punch_out:
            punch_out = timezone.now()
        
        duration = punch_out - punch_in
        total_seconds = max(duration.total_seconds(), 0)
        minutes = int(total_seconds // 60)
        return minutes

    # ========== FORMATTED punch_in_at / punch_out_at ==========
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if instance.punch_in_at:
            local_in = timezone.localtime(instance.punch_in_at)
            data['punch_in_at'] = local_in.strftime('%d %b %Y, %I:%M %p')
        
        if instance.punch_out_at:
            local_out = timezone.localtime(instance.punch_out_at)
            data['punch_out_at'] = local_out.strftime('%d %b %Y, %I:%M %p')
        
        data['status'] = instance.get_status_display()
        return data






























































# from rest_framework import serializers
# from django.utils import timezone
# from decimal import Decimal, ROUND_HALF_UP

# from Punch.models import PunchSession


# class PunchSessionSerializer(serializers.ModelSerializer):
#     employee = serializers.SerializerMethodField()
#     emp_code = serializers.SerializerMethodField()
#     department = serializers.SerializerMethodField()
#     attendance = serializers.SerializerMethodField()
    
#     # FIX: total_hours real-time calculate karo (database pe bharosa mat karo)
#     total_hours = serializers.SerializerMethodField()
#     total_minutes = serializers.SerializerMethodField()

#     class Meta:
#         model = PunchSession
#         fields = [
#             "id",
#             "employee",
#             "emp_code",
#             "department",
#             "attendance",
#             "date",
#             "punch_in_at",
#             "punch_out_at",
#             "total_hours",
#             "total_minutes",
#             "status",
#         ]

#     def get_employee(self, obj):
#         if obj.employee:
#             return getattr(obj.employee, 'full_name', str(obj.employee))
#         return "—"

#     def get_emp_code(self, obj):
#         if obj.employee:
#             return getattr(obj.employee, 'employee_code', "—")
#         return "—"

#     def get_department(self, obj):
#         if obj.employee and hasattr(obj.employee, 'department'):
#             dept = obj.employee.department
#             if dept:
#                 return getattr(dept, 'name', str(dept))
#         return "—"

#     def get_attendance(self, obj):
#         if obj.attendance:
#             return obj.attendance.get_status_display()
#         return "—"

#     # ========== FIX: Real-time total_hours calculation ==========
#     def get_total_hours(self, obj):
#         punch_in = obj.punch_in_at
#         punch_out = obj.punch_out_at
        
#         if not punch_in:
#             return Decimal("0.00")
        
#         # Agar punch out nahi hua, abhi ka time use karo
#         if not punch_out:
#             punch_out = timezone.now()
        
#         # Calculate difference
#         duration = punch_out - punch_in
#         total_seconds = max(duration.total_seconds(), 0)
#         hours = Decimal(total_seconds) / Decimal(3600)
#         hours = hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
#         return hours

#     def get_total_minutes(self, obj):
#         punch_in = obj.punch_in_at
#         punch_out = obj.punch_out_at
        
#         if not punch_in:
#             return 0
        
#         if not punch_out:
#             punch_out = timezone.now()
        
#         duration = punch_out - punch_in
#         total_seconds = max(duration.total_seconds(), 0)
#         minutes = int(total_seconds // 60)
        
#         return minutes
#     # ===========================================================

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
        
#         punch_in = instance.punch_in_at
#         punch_out = instance.punch_out_at
        
#         # ========== FIX: Local time (IST) mein convert ==========
#         if punch_in:
#             local_in = timezone.localtime(punch_in)
#             data['punch_in_date'] = local_in.strftime('%Y-%m-%d')
#             data['punch_in_time'] = local_in.strftime('%H:%M') 
#             # data['punch_in_time'] = local_in.strftime('%I:%M %p')  
#             data['punch_in_at'] = local_in.strftime('%d %b %Y, %I:%M %p')  # "25 Jun 2026, 11:20 AM"
        
#         if punch_out:
#             local_out = timezone.localtime(punch_out)
#             data['punch_out_date'] = local_out.strftime('%Y-%m-%d')
#             data['punch_out_time'] = local_out.strftime('%H:%M')
#             # data['punch_out_time'] = local_out.strftime('%I:%M %p')  
#             data['punch_out_at'] = local_out.strftime('%d %b %Y, %I:%M %p')  # "25 Jun 2026, 05:20 PM"
#         # =========================================================
        
#         data['status'] = instance.get_status_display()
        
#         return data






















































# from rest_framework import serializers
# from Punch.models import PunchSession


# class PunchSessionSerializer(serializers.ModelSerializer):
#     employee = serializers.SerializerMethodField()
#     emp_code = serializers.SerializerMethodField()
#     department = serializers.SerializerMethodField()
#     attendance = serializers.SerializerMethodField()

#     class Meta:
#         model = PunchSession
#         fields = [
#             "id",
#             "employee",
#             "emp_code",
#             "department",
#             "attendance",
#             "date",
#             "punch_in_at",
#             "punch_out_at",
#             "total_hours",
#             "total_minutes",
#             "status",
#         ]

#     def get_employee(self, obj):
#         if obj.employee:
#             return getattr(obj.employee, 'full_name', str(obj.employee))
#         return "—"

#     def get_emp_code(self, obj):
#         if obj.employee:
#             return getattr(obj.employee, 'employee_code', "—")  # <-- employee_code fix
#         return "—"

#     def get_department(self, obj):
#         if obj.employee and hasattr(obj.employee, 'department'):
#             dept = obj.employee.department
#             if dept:
#                 return getattr(dept, 'name', str(dept))
#         return "—"

#     def get_attendance(self, obj):
#         if obj.attendance:
#             return obj.attendance.get_status_display()
#         return "—"

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
        
#         punch_in = instance.punch_in_at
#         punch_out = instance.punch_out_at
        
#         data['punch_in_date'] = punch_in.strftime('%Y-%m-%d') if punch_in else ''
#         data['punch_in_time'] = punch_in.strftime('%H:%M') if punch_in else ''
        
#         data['punch_out_date'] = punch_out.strftime('%Y-%m-%d') if punch_out else ''
#         data['punch_out_time'] = punch_out.strftime('%H:%M') if punch_out else ''
        
#         data['status'] = instance.get_status_display()
        
#         return data










































































# from rest_framework import serializers
# from Punch.models import PunchSession


# class PunchSessionSerializer(serializers.ModelSerializer):
#     employee = serializers.SerializerMethodField()
#     emp_code = serializers.SerializerMethodField()
#     department = serializers.SerializerMethodField()
#     attendance = serializers.SerializerMethodField()

#     class Meta:
#         model = PunchSession
#         fields = [
#             "id",
#             "employee",
#             "emp_code",
#             "department",
#             "attendance",
#             "date",
#             "punch_in_at",
#             "punch_out_at",
#             "total_hours",
#             "total_minutes",
#             "status",
#         ]

#     def get_employee(self, obj):
#         if obj.employee:
#             return getattr(obj.employee, 'full_name', str(obj.employee))
#         return "—"

#     def get_emp_code(self, obj):
#         if obj.employee:
#             return getattr(obj.employee, 'emp_code', "—")
#         return "—"

#     def get_department(self, obj):
#         if obj.employee and hasattr(obj.employee, 'department'):
#             dept = obj.employee.department
#             if dept:
#                 return getattr(dept, 'name', str(dept))
#         return "—"

#     def get_attendance(self, obj):
#         if obj.attendance:
#             return obj.attendance.get_status_display()
#         return "—"

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
        
#         punch_in = instance.punch_in_at
#         punch_out = instance.punch_out_at
        
#         data['punch_in_date'] = punch_in.strftime('%Y-%m-%d') if punch_in else ''
#         data['punch_in_time'] = punch_in.strftime('%H:%M') if punch_in else ''
        
#         data['punch_out_date'] = punch_out.strftime('%Y-%m-%d') if punch_out else ''
#         data['punch_out_time'] = punch_out.strftime('%H:%M') if punch_out else ''
        
#         data['status'] = instance.get_status_display()
        
#         return data




































































# from rest_framework import serializers
# from .models import PunchSession


# class PunchSessionSerializer(serializers.ModelSerializer):
#     employee = serializers.SerializerMethodField()
#     emp_code = serializers.SerializerMethodField()
#     department = serializers.SerializerMethodField()
#     attendance = serializers.SerializerMethodField()

#     class Meta:
#         model = PunchSession
#         fields = [
#             "id",
#             "employee",
#             "emp_code",
#             "department",
#             "attendance",
#             "date",
#             "punch_in_at",
#             "punch_out_at",
#             "total_hours",
#             "total_minutes",
#             "status",
#         ]

#     def get_employee(self, obj):
#         if obj.employee:
#             return obj.employee.full_name if hasattr(obj.employee, 'full_name') else str(obj.employee)
#         return "—"

#     def get_emp_code(self, obj):
#         if obj.employee:
#             return getattr(obj.employee, 'emp_code', "—")
#         return "—"

#     def get_department(self, obj):
#         if obj.employee and hasattr(obj.employee, 'department'):
#             dept = obj.employee.department
#             if dept:
#                 return getattr(dept, 'name', str(dept))
#         return "—"

#     def get_attendance(self, obj):
#         if obj.attendance:
#             return obj.attendance.get_status_display()
#         return "—"

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
        
#         punch_in = instance.punch_in_at
#         punch_out = instance.punch_out_at
        
#         data['punch_in_date'] = punch_in.strftime('%Y-%m-%d') if punch_in else ''
#         data['punch_in_time'] = punch_in.strftime('%H:%M') if punch_in else ''
        
#         data['punch_out_date'] = punch_out.strftime('%Y-%m-%d') if punch_out else ''
#         data['punch_out_time'] = punch_out.strftime('%H:%M') if punch_out else ''
        
#         data['status'] = instance.get_status_display()
        
#         return data