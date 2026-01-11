from django.contrib import admin
from tenants.admin_utils import TenantAdminMixin
from .models import TaxRate, Expense, ProfitLossReport


@admin.register(TaxRate)
class TaxRateAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'tax_type', 'rate', 'is_active', 'created_at')
    list_filter = ('tax_type', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Expense)
class ExpenseAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('description', 'category', 'amount', 'tax_amount', 'total_amount', 'expense_date', 'paid')
    list_filter = ('category', 'paid', 'expense_date')
    search_fields = ('description', 'notes')
    readonly_fields = ('tax_amount', 'total_amount', 'created_at', 'updated_at')
    date_hierarchy = 'expense_date'
    
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(paid=True, payment_date=timezone.now().date())
        self.message_user(request, f'{updated} expense(s) marked as paid.')
    mark_as_paid.short_description = 'Mark selected expenses as paid'


@admin.register(ProfitLossReport)
class ProfitLossReportAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'start_date', 'end_date', 'total_revenue', 'net_profit', 'generated_at')
    list_filter = ('start_date', 'end_date')
    readonly_fields = (
        'total_revenue', 'cogs', 'operating_expenses', 'total_tax_collected',
        'total_tax_paid', 'net_tax_liability', 'gross_profit', 'net_profit', 'generated_at'
    )
    date_hierarchy = 'start_date'
