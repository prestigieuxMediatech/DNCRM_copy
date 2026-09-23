from django.db import models
from django.conf import settings
from employees.models import Employee
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models, transaction, IntegrityError
from django.db.models import Sum

from decimal import Decimal


# Create your models here.
# ─────────────────────────────────────────────
# CLIENT TABLE
# ─────────────────────────────────────────────
class Client(models.Model):
    company_name   = models.CharField(max_length=200, unique=True)
    client_name = models.CharField(max_length=150)
    email          = models.EmailField(unique=True)
    phone          = models.CharField(max_length=15)
    address        = models.TextField(blank=True)
    logo           = models.ImageField(upload_to="clients/logos/", null=True, blank=True)
    client_since   = models.DateField()
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    @property
    def total_projects(self):
        return self.projects.count()

    @property
    def completed_projects(self):
        return self.projects.filter(status="completed").count()

    @property
    def years_with_us(self):
        from django.utils import timezone
        if self.client_since:
            delta = timezone.now().date() - self.client_since
            return round(delta.days / 365, 1)
        return 0




# ─────────────────────────────────────────────
# PROJECT TABLE
# ─────────────────────────────────────────────
class Project(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed",   "Completed"),
        ("on_hold",     "On Hold"),
        ("cancelled",    "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low",    "Low"),
        ("medium", "Medium"),
        ("high",   "High"),
    ]

    project_name = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES,   default="pending", db_index=True)
    priority     = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium", db_index=True)
    client       = models.ForeignKey(
                       Client,
                       on_delete=models.PROTECT,
                       related_name="projects",
                        db_index=True
                   )
    budget       = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_created",
        db_index=True
    )
    employees = models.ManyToManyField(
        Employee,
        related_name="assigned_projects",
        blank=True
    )
    deadline = models.DateField(null=True, blank=True, db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_name} ({self.get_status_display()})"


     # ── Ordering & Indexing ──
    class Meta:
        ordering = ['-created_at']  # Naye projects pehle
        indexes = [
            # Composite index: Status + Date (sabse common filter combo)
            models.Index(fields=['status', '-created_at'], name='status_created_idx'),
            
            # Composite index: Client + Status (client ke projects filter karte time)
            models.Index(fields=['client', 'status'], name='client_status_idx'),
            
            # Composite index: Priority + Deadline (dashboard sorting)
            models.Index(fields=['priority', 'deadline'], name='prio_deadline_idx'),
            
            # Composite index: Created_by + Status (admin dashboard ke liye)
            models.Index(fields=['created_by', '-created_at'], name='creator_created_idx'),
        ]

    # ── Validation ──
    def clean(self):
        super().clean()
        if self.budget is not None and self.budget < 0:
            raise ValidationError({"budget": "Budget negative nahi ho sakta."})
        
        if self.deadline and self.deadline < timezone.now().date():
            raise ValidationError({"deadline": "Deadline aaj se pehle ki date nahi ho sakti."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)









# ─── 1. SERVICE CATALOG (Menu Card) ───
class ServiceCatalog(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ─── 2. INVOICE (Bill Header) ───
class Invoice(models.Model):

    # 🔒 In status mein invoice lock ho jayegi (edit nahi hogi)
    LOCKED_STATUSES = ('paid', 'cancelled')

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    CURRENCY_CHOICES = [
        ('INR', '₹ INR'),
        ('USD', '$ USD'),
        ('EUR', '€ EUR'),
    ]

    # ✅ EDITABLE INVOICE NUMBER:
    # Blank chhodoge toh auto-generate hoga. 
    # Kuch manual type karoge toh custom number save hoga (Create & Edit dono mein).
    invoice_number = models.CharField(
        max_length=50,
        unique=False,
        blank=True,
        null=True,
        help_text="Khali chhodo toh auto-generate hoga. Direct edit karke custom number bhi daal sakte ho."
    )

    client = models.ForeignKey(
        'Client',
        on_delete=models.PROTECT,
        related_name="invoices"
    )

    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    notes = models.TextField(blank=True)

    # ─────────────────────────────────────────────────────────
    # 🚨 SOFT DELETE & AUDIT LOG FIELDS (Tracking Missing Invoices)
    # ─────────────────────────────────────────────────────────
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_invoices"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        return f"{self.invoice_number or 'DRAFT'} - {self.client.company_name}"

    # ─────────────────────────────────────────────────────────
    # 🗑️ SOFT DELETE METHOD
    # ─────────────────────────────────────────────────────────
    def soft_delete(self, user=None):
        """Invoice ko permanent destroy karne ke bajaye soft delete mark karega"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user and user.is_authenticated:
            self.deleted_by = user
        self.status = 'cancelled'
        self.save()

    # ─────────────────────────────────────────────────────────
    # ✅ SAVE: Custom vs Auto-number handling
    # ─────────────────────────────────────────────────────────
    def save(self, *args, **kwargs):
        auto_number = not self.invoice_number

        if not auto_number:
            # User ne manual edit karke number dala hai -> Seedha save karo
            return super().save(*args, **kwargs)

        # Blank chhota hai -> Auto-generate mode (Clash handle karne ke liye 3 retry)
        for attempt in range(3):
            try:
                with transaction.atomic():
                    self.invoice_number = self._generate_invoice_number()
                    if kwargs.get('update_fields'):
                        kwargs['update_fields'] = list(kwargs['update_fields']) + ['invoice_number']
                    super().save(*args, **kwargs)
                return
            except IntegrityError:
                self.invoice_number = ''  # Retry with fresh number
                if attempt == 2:
                    raise IntegrityError("Unique invoice number generate nahi ho paya. Dobara try karo.")

    # ─────────────────────────────────────────────────────────
    # Number generator: MAX Number Check (Including Deleted Invoices)
    # ─────────────────────────────────────────────────────────
    @classmethod
    def _generate_invoice_number(cls):
        current_year = timezone.now().year
        prefix = f"INV-{current_year}-"

        # Deleted aur Active dono invoices scan karega taaki duplicate na bane
        all_invoices = cls.objects.filter(
            invoice_number__startswith=prefix
        ).exclude(invoice_number='')

        max_num = 0
        for inv in all_invoices:
            try:
                num_part = int(inv.invoice_number.split('-')[-1])
                if num_part > max_num:
                    max_num = num_part
            except (ValueError, IndexError):
                continue

        new_num = max_num + 1
        return f"{prefix}{new_num:04d}"

    # ─────────────────────────────────────────────────────────
    # Items ka total calculation
    # ─────────────────────────────────────────────────────────
    def calculate_total(self):
        total = self.items.aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        type(self).objects.filter(pk=self.pk).update(total_amount=total)
        self.total_amount = total
        return total

    @property
    def is_locked(self):
        return self.status in self.LOCKED_STATUSES


# ─── 3. INVOICE ITEM (Bill Ki List) ───
class InvoiceItem(models.Model):
    # Kis invoice ka item hai
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )
    
    # Kis project ka hai (optional)
    project = models.ForeignKey(
        'Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_items"
    )
    
    # Kaunsi service select ki (optional — reference ke liye)
    service = models.ForeignKey(
        ServiceCatalog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_items"
    )
    
    # 🔥 Yahan service ka naam likhna hai jo bill pe print hoga
    service_name = models.CharField(max_length=255)
   
    
    # 🔥 Seedha final amount daalo — koi multiply nahi
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.calculate_total()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.calculate_total()

    def __str__(self):
        return f"{self.service_name} - ₹{self.amount}"
