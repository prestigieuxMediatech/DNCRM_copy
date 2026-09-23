from rest_framework import serializers
from .models import Project, Client, ServiceCatalog, Invoice, InvoiceItem

from employees.models import Employee
from django.core.validators import FileExtensionValidator   # 🟢 YEH ADD KAR


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "company_name"]



# ─── NEW: Full Client CRUD — alag name se ───
class ClientDetailSerializer(serializers.ModelSerializer):
    """Client list/create/update/delete ke liye — alag se banaya hai"""


        # 🟢 YEH FIELD EXPLICITLY DECLARE KAR — pehle auto tha, ab validation ke saath
    logo = serializers.ImageField(
        required=False,
        allow_null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
        ]
    )




    logo_url = serializers.SerializerMethodField()
    total_projects = serializers.IntegerField(read_only=True)
    completed_projects = serializers.IntegerField(read_only=True)
    years_with_us = serializers.FloatField(read_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "company_name",
            "client_name",
            "email",
            "phone",
            "address",
            "logo",
            "logo_url",
            "client_since",
            "is_active",
            "total_projects",
            "completed_projects",
            "years_with_us",
            "created_at",
            "updated_at",
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            return self.context.get('request').build_absolute_uri(obj.logo.url)
        return ""


     # 🟢 NAYA METHOD — size validation (2MB limit)
    def validate_logo(self, value):
            if value and value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError("Logo must be under 2MB")
            return value



    

    def validate_email(self, value):
        if Client.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


   

    

    def validate_company_name(self, value):
        if Client.objects.filter(company_name=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Company name already exists.")
        return value









class ServiceCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCatalog
        fields = ['id', 'name', 'description', 'base_price', 'is_active', 'created_at']

# class InvoiceItemSerializer(serializers.ModelSerializer):
#     project_name = serializers.CharField(source='project.project_name', read_only=True)
#     service_catalog_name = serializers.CharField(source='service.name', read_only=True)

#     class Meta:
#         model = InvoiceItem
#         fields = [
#             'id', 'invoice', 'project', 'project_name', 
#             'service', 'service_catalog_name', 'service_name', 
#             'amount'
#         ]


# class InvoiceSerializer(serializers.ModelSerializer):
#     client_name = serializers.CharField(source='client.company_name', read_only=True)
#     client_email = serializers.CharField(source='client.email', read_only=True)
#     items = InvoiceItemSerializer(many=True, read_only=True)
#     item_count = serializers.IntegerField(source='items.count', read_only=True)
#     deleted_by_name = serializers.CharField(source='deleted_by.username', read_only=True, default=None)

#     class Meta:
#         model = Invoice
#         fields = [
#             'id', 'invoice_number', 'client', 'client_name', 'client_email',
#             'issue_date', 'due_date', 'status', 'currency',
#             'total_amount', 'notes', 'items', 'item_count',
#             'is_deleted', 'deleted_at', 'deleted_by', 'deleted_by_name',
#             'created_at', 'updated_at'
#         ]
#         read_only_fields = ['is_deleted', 'deleted_at', 'deleted_by']
        
#         # invoice_number blank allowed → auto-generate (model handle karta hai)
#         extra_kwargs = {
#             'invoice_number': {'required': False, 'allow_blank': True},
#         }

#     # ─────────────────────────────────────────────────────────
#     # ✅ Manual number duplicate check (Active + Soft Deleted check)
#     # ─────────────────────────────────────────────────────────
#     def validate_invoice_number(self, value):
#         value = (value or '').strip()
#         if not value:
#             return value
        
#         # Duplicate check across ALL invoices (including soft-deleted ones)
#         qs = Invoice.objects.filter(invoice_number=value)
#         if self.instance:
#             qs = qs.exclude(pk=self.instance.pk)
            
#         if qs.exists():
#             raise serializers.ValidationError(
#                 f"'{value}' ye invoice number pehle se exist karta hai (Active ya Deleted history mein)."
#             )
#         return value

#     # ─────────────────────────────────────────────────────────
#     # 🔒 Paid / Cancelled invoice edit-block
#     # ─────────────────────────────────────────────────────────
#     def validate(self, attrs):
#         if self.instance and self.instance.is_locked:
#             raise serializers.ValidationError({
#                 'detail': f"'{self.instance.get_status_display()}' invoice edit nahi ho sakti."
#             })
#         return attrs





# class InvoiceItemSerializer(serializers.ModelSerializer):
#     project_name = serializers.CharField(source='project.project_name', read_only=True)
#     service_catalog_name = serializers.CharField(source='service.name', read_only=True)

#     class Meta:
#         model = InvoiceItem
#         fields = [
#             'id', 'invoice', 'project', 'project_name', 
#             'service', 'service_catalog_name', 'service_name', 
#             'amount'
#         ]


# class InvoiceSerializer(serializers.ModelSerializer):
#     client_name = serializers.CharField(source='client.company_name', read_only=True)
#     client_email = serializers.CharField(source='client.email', read_only=True)
#     items = InvoiceItemSerializer(many=True, read_only=True)
#     item_count = serializers.IntegerField(source='items.count', read_only=True)
#     deleted_by_name = serializers.CharField(source='deleted_by.username', read_only=True, default=None)

#     class Meta:
#         model = Invoice
#         fields = [
#             'id', 'invoice_number', 'client', 'client_name', 'client_email',
#             'issue_date', 'due_date', 'status', 'currency',
#             'total_amount', 'notes', 'items', 'item_count',
#             'is_deleted', 'deleted_at', 'deleted_by', 'deleted_by_name',
#             'created_at', 'updated_at'
#         ]
#         read_only_fields = ['is_deleted', 'deleted_at', 'deleted_by']
        
#         extra_kwargs = {
#             'invoice_number': {'required': False, 'allow_blank': True},
#         }

#     def validate_invoice_number(self, value):
#         value = (value or '').strip()
#         if not value:
#             return value
        
#         # Duplicate check across ALL invoices (including soft-deleted ones)
#         qs = Invoice.objects.filter(invoice_number__iexact=value)
#         if self.instance:
#             qs = qs.exclude(pk=self.instance.pk)
            
#         if qs.exists():
#             raise serializers.ValidationError(
#                 f"'{value}' yeh invoice number pehle se exist karta hai (Active ya Deleted history mein)."
#             )
#         return value

#     def validate(self, attrs):
#         if self.instance and self.instance.is_locked:
#             raise serializers.ValidationError({
#                 'detail': f"'{self.instance.get_status_display()}' invoice edit nahi ho sakti."
#             })
#         return attrs


















# class InvoiceItemSerializer(serializers.ModelSerializer):
#     project_name = serializers.CharField(source='project.project_name', read_only=True)
#     service_catalog_name = serializers.CharField(source='service.name', read_only=True)

#     class Meta:
#         model = InvoiceItem
#         fields = [
#             'id', 'invoice', 'project', 'project_name', 
#             'service', 'service_catalog_name', 'service_name', 
#             'amount'
#         ]


# class InvoiceSerializer(serializers.ModelSerializer):
#     client_name = serializers.CharField(source='client.company_name', read_only=True)
#     client_email = serializers.CharField(source='client.email', read_only=True)
#     items = InvoiceItemSerializer(many=True, read_only=True)
#     item_count = serializers.IntegerField(source='items.count', read_only=True)
#     deleted_by_name = serializers.CharField(source='deleted_by.username', read_only=True, default=None)

#     class Meta:
#         model = Invoice
#         fields = [
#             'id', 'invoice_number', 'client', 'client_name', 'client_email',
#             'issue_date', 'due_date', 'status', 'currency',
#             'total_amount', 'notes', 'items', 'item_count',
#             'is_deleted', 'deleted_at', 'deleted_by', 'deleted_by_name',
#             'created_at', 'updated_at'
#         ]
#         read_only_fields = ['is_deleted', 'deleted_at', 'deleted_by']
        
#         extra_kwargs = {
#             'invoice_number': {'required': False, 'allow_blank': True},
#         }

#     def validate_invoice_number(self, value):
#         value = (value or '').strip()
#         if not value:
#             return value
        
#         # Admin duplicate check ONLY against active (non-deleted) invoices
#         qs = Invoice.objects.filter(invoice_number__iexact=value, is_deleted=False)
#         if self.instance:
#             qs = qs.exclude(pk=self.instance.pk)
            
#         if qs.exists():
#             raise serializers.ValidationError(
#                 f"Invoice number '{value}' active invoices mein pehle se present hai."
#             )
#         return value    










class InvoiceItemSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    service_catalog_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'invoice', 'project', 'project_name', 
            'service', 'service_catalog_name', 'service_name', 
            'amount'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.company_name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)
    deleted_by_name = serializers.CharField(source='deleted_by.username', read_only=True, default=None)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client', 'client_name', 'client_email',
            'issue_date', 'due_date', 'status', 'currency',
            'total_amount', 'notes', 'items', 'item_count',
            'is_deleted', 'deleted_at', 'deleted_by', 'deleted_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['is_deleted', 'deleted_at', 'deleted_by']
        
        extra_kwargs = {
            'invoice_number': {
                'validators': [],
                'required': False, 
                'allow_blank': True
            },
        }

    def validate_invoice_number(self, value):
        value = (value or '').strip()
        if not value:
            return value
        
        # Check matching invoice_number only in ACTIVE (is_deleted=False) invoices
        qs = Invoice.objects.filter(invoice_number__iexact=value, is_deleted=False)
        
        # ✅ FIX: Update ke time par wahi active invoice exclude ho jayegi
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
            
        if qs.exists():
            raise serializers.ValidationError(
                f"Invoice number '{value}' doosri active invoice mein already use ho raha hai."
            )
        return value























































class EmployeeMiniSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ["id", "name", "employee_code", "department"]

    def get_name(self, obj):
        return obj.full_name

    def get_department(self, obj):
        if obj.department:
            return obj.department.name
        return "—"


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    employees = EmployeeMiniSerializer(many=True, read_only=True)
    team_members_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "project_name",
            "description",
            "status",
            "priority",
            "client",
            "client_name",
            "budget",
            "created_by",
            "created_by_email",
            "employees",
            "employee_ids",
            "team_members_count",
            "deadline",
            "created_at",
            "updated_at",
        ]

    def get_client_name(self, obj):
        return obj.client.company_name if obj.client else "—"

    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else "—"

    def get_team_members_count(self, obj):
        return obj.employees.count()

    def create(self, validated_data):
        employee_ids = validated_data.pop('employee_ids', [])
        project = Project.objects.create(**validated_data)
        if employee_ids:
            project.employees.set(employee_ids)
        return project

    def update(self, instance, validated_data):
        employee_ids = validated_data.pop('employee_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if employee_ids is not None:
            instance.employees.set(employee_ids)
        return instance




































































# from rest_framework import serializers
# from .models import Project, Client
# from employees.models import Employee


# class ClientSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Client
#         fields = ["id", "company_name"]


# class EmployeeMiniSerializer(serializers.ModelSerializer):
#     name = serializers.SerializerMethodField()
#     department = serializers.SerializerMethodField()

#     class Meta:
#         model = Employee
#         fields = ["id", "name", "employee_code", "department"]

#     def get_name(self, obj):
#         return obj.full_name

#     def get_department(self, obj):
#         if obj.department:
#             return obj.department.name
#         return "—"


# class ProjectSerializer(serializers.ModelSerializer):
#     client_name = serializers.SerializerMethodField()
#     created_by_email = serializers.SerializerMethodField()
#     employee_ids = serializers.ListField(
#         child=serializers.IntegerField(),
#         write_only=True,
#         required=False
#     )
#     employees = EmployeeMiniSerializer(many=True, read_only=True)
#     team_members_count = serializers.SerializerMethodField()

#     class Meta:
#         model = Project
#         fields = [
#             "id",
#             "project_name",
#             "description",
#             "status",
#             "priority",
#             "client",
#             "client_name",
#             "budget",
#             "created_by",
#             "created_by_email",
#             "employees",
#             "employee_ids",
#             "team_members_count",
#             "created_at",
#             "updated_at",
#         ]

#     def get_client_name(self, obj):
#         return obj.client.company_name if obj.client else "—"

#     def get_created_by_email(self, obj):
#         return obj.created_by.email if obj.created_by else "—"

#     def get_team_members_count(self, obj):
#         return obj.employees.count()

#     def create(self, validated_data):
#         employee_ids = validated_data.pop('employee_ids', [])
#         project = Project.objects.create(**validated_data)
#         if employee_ids:
#             project.employees.set(employee_ids)
#         return project

#     def update(self, instance, validated_data):
#         employee_ids = validated_data.pop('employee_ids', None)
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         if employee_ids is not None:
#             instance.employees.set(employee_ids)
#         return instance