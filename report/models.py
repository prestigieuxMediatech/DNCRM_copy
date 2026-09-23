from django.conf import settings
from django.db import models

from employees.models import Employee
from django.core.exceptions import ValidationError



class Leave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ("sick_leave", "Sick Leave"),
        ("casual_leave", "Casual Leave"),
        ("emergency_leave", "Emergency Leave"),
        ("paid_leave", "Paid Leave"),        
        ("unpaid_leave", "Unpaid Leave"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leaves",
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leaves",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Leave"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_leave_type_display()}"




def validate_image_size(value):
    limit = 5 * 1024 * 1024   # 5MB
    if value.size > limit:
        raise ValidationError("Image size must be under 5MB.")


    


class Report(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    subject = models.CharField(max_length=200)
    work_summary = models.TextField()
    attachment = models.ImageField(
        upload_to="report_attachment/%Y/%m/",
        blank=True,
        null=True,
        validators=[validate_image_size] 
    )
    report_date = models.DateField(db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Report"
        ordering = ["-report_date", "-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "report_date"],
                name="unique_report_per_employee_date",
            ),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.report_date}"
