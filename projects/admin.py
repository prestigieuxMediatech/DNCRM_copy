from django.contrib import admin
from.models import Client, Project,  ServiceCatalog, Invoice, InvoiceItem

# Register your models here.

admin.site.register(Client)
admin.site.register(Project)




@admin.register(ServiceCatalog)
class ServiceCatalogAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'is_active']
    search_fields = ['name']

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['project', 'service', 'service_name', 'amount']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'total_amount', 'issue_date']
    search_fields = ['invoice_number', 'client__company_name']
    readonly_fields = ['invoice_number', 'total_amount']
    inlines = [InvoiceItemInline]
    date_hierarchy = 'issue_date'

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['service_name', 'amount', 'invoice']
    search_fields = ['service_name']