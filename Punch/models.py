from django.db import models

from employees.models import Employee


class PunchSession(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("auto_closed", "Auto Closed"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="punch_sessions",
    )

    attendance = models.OneToOneField(
    "attendance.Attendance",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="punch_session",
)
  
    date = models.DateField()
    punch_in_at = models.DateTimeField()
    punch_out_at = models.DateTimeField(null=True, blank=True)
    total_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    total_minutes = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PunchSession"
        ordering = ["-date", "-punch_in_at"]
        indexes = [
            models.Index(fields=["employee", "date"]),
            models.Index(fields=["status"]),
             models.Index(fields=["punch_in_at"]),
        ]
        constraints = [
        models.UniqueConstraint(
            fields=["employee", "date"],
            name="unique_employee_daily_session",
        )
    ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.get_status_display()}"





      








#   attendance = models.ForeignKey(
#         "attendance.Attendance",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="punch_sessions",
#     )