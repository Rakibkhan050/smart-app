from django.contrib import admin
from tenants.admin_utils import TenantAdminMixin
from .models import Receipt, Payment


@admin.register(Payment)
class PaymentAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('payment_id', 'provider', 'status', 'amount', 'currency', 'created_at')
    search_fields = ('payment_id', 'provider')
    list_filter = ('provider', 'status')
    readonly_fields = ('created_at',)


@admin.register(Receipt)
class ReceiptAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('invoice_no', 'payment_id', 'amount', 'vat_amount', 'created_at')
    search_fields = ('invoice_no', 'payment_id')
    list_filter = ()
    readonly_fields = ('created_at',)
