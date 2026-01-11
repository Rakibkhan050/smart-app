from django.contrib import admin
from tenants.admin_utils import TenantAdminMixin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'status', 'customer', 'subtotal', 'tax_amount', 'shipping_fee', 'total', 'created_at')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price')
