from django.db import models
from accounts.models import User
import uuid
import re



# ─────────────────────────────────────────────
class Department(models.Model):
    name       = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
class Designation(models.Model):
    title      = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="designations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────
class Employee(models.Model):
    EMPLOYMENT_STATUS = [
        ("ACTIVE",   "Active"),
        ("INACTIVE", "Inactive"),
        ("RESIGNED", "Resigned"),
    ]

    # ── Auth link ──
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )

    # ── Personal info ──
    first_name        = models.CharField(max_length=100)
    last_name         = models.CharField(max_length=100)
    phone             = models.CharField(max_length=15, unique=True)
    profile_image     = models.ImageField(upload_to="profiles/", null=True, blank=True)
    address           = models.TextField(blank=True)
    date_of_birth     = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)

    # ── Company info ──
    employee_code     = models.CharField(max_length=20, unique=True, blank=True)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default="ACTIVE")
    department        = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="employees"
    )
    designation       = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="employees"
    )
    joining_date      = models.DateField()
    bank_account = models.CharField(max_length=50, blank=True)
    bank_name     = models.CharField(max_length=100, blank=True)
    salary            = models.DecimalField(max_digits=10, decimal_places=2)

    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    # ── Methods (FIELDS KE BAAD) ──
    @classmethod
    def next_employee_code(cls):
        max_num = 0
        for code in cls.objects.values_list("employee_code", flat=True):
            match = re.fullmatch(r"EMP(\d+)", code or "")
            if match:
                max_num = max(max_num, int(match.group(1)))
        return f"EMP{max_num + 1:03d}"

    def save(self, *args, **kwargs):
        if not self.employee_code:
            self.employee_code = self.next_employee_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} [{self.employee_code}]"

    @property
    def email(self):
        return self.user.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def designation_name(self):
        if self.designation:
            return getattr(self.designation, 'title', None) or getattr(self.designation, 'name', '') or str(self.designation)
        return ""





























































# # Create your models here.
# from django.db import models
# from accounts.models import User
# import uuid


# # class Department(models.Model):
# #     name = models.CharField(max_length=100, unique=True)

# #     def __str__(self):
# #         return self.name


# # class Designation(models.Model):
# #     title = models.CharField(max_length=100, unique=True)

# #     def __str__(self):
# #         return self.title
    




# class Department(models.Model):
#     name       = models.CharField(max_length=100, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name



# class Designation(models.Model):
#     title      = models.CharField(max_length=100, unique=True)
#     department = models.ForeignKey(
#         Department,
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#         related_name="designations"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title
    


# # ─────────────────────────────────────────────
# # EMPLOYEE MODEL  →  sirf HR / business data
# # ─────────────────────────────────────────────
# class Employee(models.Model):
#     # ── Link to User (OneToOne = no duplicate rows) ──
#     user = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name="employee_profile"
#     )

#     # ── Personal info (NOT in User table) ──
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     phone          = models.CharField(max_length=15, unique=True)
#     profile_image  = models.ImageField(upload_to="profiles/", null=True, blank=True)
#     address        = models.TextField(blank=True)
#     date_of_birth = models.DateField(
#     null=True,
#     blank=True
# )

  

#     # ── Company info ──
#     EMPLOYMENT_STATUS = [
#         ("ACTIVE", "Active"),
#         ("INACTIVE", "Inactive"),
#         ("RESIGNED", "Resigned"),
# ]

#     employment_status = models.CharField(
#         max_length=20,
#         choices=EMPLOYMENT_STATUS,
#         default="ACTIVE"
# )
    
#     emergency_contact = models.CharField(
#     max_length=15,
#     blank=True
# )
    
#        # Option 1 — Simple (EMP001, EMP002)
#     employee_code = models.CharField(
#         max_length=20, 
#         unique=True, 
#         blank=True  # auto generate hoga
#     )
    
#     def save(self, *args, **kwargs):
#         if not self.employee_code:
#             # Last employee ka code dhundo, +1 karo
#             last = Employee.objects.order_by('id').last()
#             num = (last.id + 1) if last else 1
#             self.employee_code = f"EMP{num:03d}"  # EMP001
#         super().save(*args, **kwargs)


#     department = models.ForeignKey(
#         Department,
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#         related_name="employees"
#     )
#     designation    = models.ForeignKey(
#         Designation,
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#         related_name="employees"
#     )
#     joining_date   = models.DateField()
#     salary         = models.DecimalField(max_digits=10, decimal_places=2)

#     created_at     = models.DateTimeField(auto_now_add=True)
#     updated_at     = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.employee_name} [{self.employee_code}]"

#     # Helper: get email from linked User (no duplication)
#     @property
#     def email(self):
#         return self.user.email












# # class Employee(models.Model):

# #     user = models.OneToOneField(
# #         User,
# #         on_delete=models.CASCADE
# #     )

# #     employee_name = models.CharField(
# #         max_length=150
# #     )

# #     employee_email = models.EmailField()

# #     profile_image = models.ImageField(
# #         upload_to='employees/',
# #         blank=True,
# #         null=True
# #     )


# #     department = models.ForeignKey(
# #         Department,
# #         on_delete=models.SET_NULL,
# #         null=True
# #     )

# #     designation = models.ForeignKey(
# #         Designation,
# #         on_delete=models.SET_NULL,
# #         null=True
# #     )

# #     phone = models.CharField(max_length=15)

# #     joining_date = models.DateField()

# #     salary = models.DecimalField(
# #         max_digits=10,
# #         decimal_places=2
# #     )

# #     address = models.TextField(
# #         blank=True,
# #         null=True
# #     )
