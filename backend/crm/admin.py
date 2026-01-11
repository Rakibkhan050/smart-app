from django.contrib import admin
from tenants.admin_utils import TenantAdminMixin
from .models import Customer, LoyaltyPoint, Supplier, LoyaltyTransaction, PurchaseHistory


@admin.register(Customer)
class CustomerAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'get_loyalty_points', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ()
    readonly_fields = ('created_at', 'updated_at')

    def get_loyalty_points(self, obj):
        try:
            return obj.loyalty.points
        except LoyaltyPoint.DoesNotExist:
            return 0
    get_loyalty_points.short_description = 'Loyalty Points'


@admin.register(LoyaltyPoint)
class LoyaltyPointAdmin(admin.ModelAdmin):
    list_display = ('customer', 'points', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'transaction_type', 'points', 'reason', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('customer__first_name', 'customer__last_name', 'reason')
    readonly_fields = ('created_at',)


@admin.register(PurchaseHistory)
class PurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order', 'amount', 'loyalty_earned', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer__first_name', 'customer__last_name')
    readonly_fields = ('created_at',)


@admin.register(Supplier)
class SupplierAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'contact', 'phone', 'payment_status', 'created_at')
    search_fields = ('name', 'contact', 'phone')