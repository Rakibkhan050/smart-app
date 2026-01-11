from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import (
    Tenant, TenantOperatingHours, TenantBankAccount, StorefrontConfig
)


class TenantOperatingHoursInline(admin.TabularInline):
    """Inline editing of operating hours"""
    model = TenantOperatingHours
    extra = 0
    fields = ('day_of_week', 'is_open', 'opening_time', 'closing_time')


class TenantBankAccountInline(admin.StackedInline):
    """Inline editing of bank account"""
    model = TenantBankAccount
    extra = 0
    fields = ('account_holder_name', 'account_type', 'bank_name', 'iban', 'is_verified')

class StorefrontConfigInline(admin.StackedInline):
    """Inline editing of storefront/PWA settings"""
    model = StorefrontConfig
    extra = 0
    fields = (
        'app_name', 'short_name', 'theme_color', 'background_color', 'display',
        'start_url', 'scope', 'icon_url', 'site_domain', 'offline_enabled',
        'seo_title', 'seo_description'
    )


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Master admin interface for managing all tenants (businesses)"""
    
    list_display = [
        'name', 'registration_id', 'category_tag', 'owner_email', 'subscription_status',
        'total_sales_display', 'is_approved_badge', 'verification_status_badge', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'is_approved', 'verification_status', 'subscription_tier',
        'category', 'created_at'
    ]
    
    search_fields = [
        'name', 'registration_id', 'owner_email', 'owner_phone', 'business_phone'
    ]
    
    readonly_fields = [
        'id', 'slug', 'registration_id', 'total_sales', 'total_commission',
        'total_customers', 'total_orders', 'average_order_value', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Business Information', {
            'fields': ('id', 'name', 'slug', 'registration_id', 'category', 'description')
        }),
        ('Branding', {
            'fields': ('logo', 'banner_image', 'color_primary', 'color_secondary')
        }),
        ('Contact Information', {
            'fields': (
                'owner_name', 'owner_email', 'owner_phone', 'business_phone',
                'business_address', 'business_latitude', 'business_longitude'
            )
        }),
        ('Legal & Compliance', {
            'fields': (
                'privacy_policy', 'terms_of_service', 'return_policy',
                'business_registration_document', 'tax_id'
            ),
            'classes': ('collapse',)
        }),
        ('Status & Verification', {
            'fields': (
                'is_active', 'is_approved', 'verification_status',
                'is_subscription_active', 'subscription_tier'
            )
        }),
        ('Financial', {
            'fields': (
                'commission_rate', 'total_sales', 'total_commission', 'total_payouts',
                'currency'
            ),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('timezone', 'language'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': (
                'total_customers', 'total_orders', 'average_order_value',
                'last_activity'
            ),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [StorefrontConfigInline, TenantOperatingHoursInline, TenantBankAccountInline]
    
    actions = ['approve_business', 'reject_business', 'activate_business', 'deactivate_business']
    
    def get_queryset(self, request):
        """Master admin sees all tenants"""
        qs = super().get_queryset(request)
        # Master admin can see all, business owners see only their own
        if request.user.is_superuser or (hasattr(request.user, 'is_master_admin') and request.user.is_master_admin()):
            return qs
        # Filter by business owner
        if hasattr(request.user, 'business_profile'):
            return qs.filter(id=request.user.business_profile.tenant.id)
        return qs.none()
    
    def category_tag(self, obj):
        """Display category with color"""
        colors = {
            'agriculture': '#10b981',
            'grocery': '#3b82f6',
            'restaurant': '#f59e0b',
            'pharmacy': '#ef4444',
            'fashion': '#ec4899',
            'electronics': '#6366f1',
            'hardware': '#8b5cf6',
        }
        color = colors.get(obj.category, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_tag.short_description = 'Category'
    
    def total_sales_display(self, obj):
        """Display total sales with currency"""
        return format_html(
            '<strong>{} {}</strong>',
            obj.currency,
            f'{float(obj.total_sales):,.2f}'
        )
    total_sales_display.short_description = 'Total Sales'
    
    def is_approved_badge(self, obj):
        """Display approval status badge"""
        if obj.is_approved:
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 3px;">✓ Approved</span>'
            )
        return format_html(
            '<span style="background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 3px;">✗ Not Approved</span>'
        )
    is_approved_badge.short_description = 'Approval'
    
    def subscription_status(self, obj):
        """Display subscription status"""
        colors = {
            'basic': '#3b82f6',
            'professional': '#10b981',
            'enterprise': '#f59e0b',
        }
        color = colors.get(obj.subscription_tier, '#6b7280')
        active = '✓ Active' if obj.is_subscription_active else '✗ Inactive'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{} - {}</span>',
            color,
            obj.get_subscription_tier_display(),
            active
        )
    subscription_status.short_description = 'Subscription'
    
    def verification_status_badge(self, obj):
        """Display verification status"""
        colors = {
            'pending': '#f59e0b',
            'verified': '#10b981',
            'rejected': '#ef4444',
        }
        color = colors.get(obj.verification_status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_verification_status_display()
        )
    verification_status_badge.short_description = 'Verification'
    
    def approve_business(self, request, queryset):
        """Action to approve businesses"""
        updated = queryset.update(is_approved=True, verification_status='verified')
        self.message_user(request, f'{updated} business(es) approved.')
    approve_business.short_description = "✓ Approve selected businesses"
    
    def reject_business(self, request, queryset):
        """Action to reject businesses"""
        updated = queryset.update(is_approved=False, verification_status='rejected')
        self.message_user(request, f'{updated} business(es) rejected.')
    reject_business.short_description = "✗ Reject selected businesses"
    
    def activate_business(self, request, queryset):
        """Action to activate businesses"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} business(es) activated.')
    activate_business.short_description = "▶ Activate selected businesses"
    
    def deactivate_business(self, request, queryset):
        """Action to deactivate businesses"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} business(es) deactivated.')
    deactivate_business.short_description = "⏸ Deactivate selected businesses"


@admin.register(TenantOperatingHours)
class TenantOperatingHoursAdmin(admin.ModelAdmin):
    """Admin for operating hours"""
    list_display = ['tenant', 'day_of_week', 'is_open', 'opening_time', 'closing_time']
    list_filter = ['day_of_week', 'is_open', 'tenant']
    search_fields = ['tenant__name']


@admin.register(TenantBankAccount)
class TenantBankAccountAdmin(admin.ModelAdmin):
    """Admin for bank accounts"""
    list_display = ['tenant', 'account_holder_name', 'bank_name', 'account_type', 'is_verified']
    list_filter = ['is_verified', 'account_type', 'created_at']
    search_fields = ['tenant__name', 'account_holder_name', 'iban']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Account Holder', {
            'fields': ('tenant', 'account_holder_name')
        }),
        ('Account Details', {
            'fields': ('account_type', 'account_number', 'bank_name', 'bank_code')
        }),
        ('International Details', {
            'fields': ('iban', 'swift_code', 'currency'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

