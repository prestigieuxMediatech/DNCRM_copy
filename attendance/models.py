from django.db import models

from employees.models import Employee


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("half_day", "Half Day"),
        ("absent", "Absent"),
        ("leave", "Leave"),
        ("weekly_off", "Weekly Off"),
        ("holiday", "Holiday"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    leave_request = models.ForeignKey(
        "report.Leave",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances",
    )
    date = models.DateField()
    day = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    remarks = models.CharField(max_length=255, blank=True)
    working_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Attendance"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"],
                name="unique_attendance_per_employee_date",
            ),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.get_status_display()}"
