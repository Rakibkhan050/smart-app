from django.contrib import admin
from tenants.admin_utils import TenantAdminMixin
from .models import Product


@admin.register(Product)
class ProductAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'sku', 'brand', 'sell_price', 'cost_price', 'created_at')
    search_fields = ('name', 'sku', 'brand')
    list_filter = ('brand',)
    readonly_fields = ('created_at', 'updated_at')
