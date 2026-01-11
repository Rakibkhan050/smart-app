from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.db.models import Q
from .models import (
    CustomUser, CustomerProfile, BusinessOwnerProfile,
    UserLoginHistory, UserNotificationPreferences
)


class CustomUserAdmin(DjangoUserAdmin):
    """Extended user admin with global search capabilities"""
    
    list_display = [
        'username', 'registration_id', 'get_full_name', 'user_type_badge',
        'email', 'phone_number', 'tenant_name', 'verified_badge', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'user_type', 'is_active', 'is_verified', 'email_verified',
        'phone_verified', 'tenant', 'created_at'
    ]
    
    search_fields = [
        'username', 'email', 'phone_number', 'registration_id',
        'first_name', 'last_name', 'tenant__name'
    ]
    
    readonly_fields = [
        'id', 'registration_id', 'date_joined', 'created_at', 'updated_at'
    ]
    
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('User Type & Tenant', {
            'fields': ('user_type', 'tenant', 'registration_id')
        }),
        ('Profile Information', {
            'fields': (
                'phone_number', 'profile_picture', 'date_of_birth', 'gender', 'bio'
            ),
            'classes': ('collapse',)
        }),
        ('Address & Location', {
            'fields': (
                'address_line_1', 'address_line_2', 'city', 'state',
                'postal_code', 'country', 'latitude', 'longitude'
            ),
            'classes': ('collapse',)
        }),
        ('Account Status & Verification', {
            'fields': (
                'is_verified', 'email_verified', 'phone_verified',
                'email_verification_token', 'phone_verification_token'
            ),
            'classes': ('collapse',)
        }),
        ('Activity & Security', {
            'fields': ('last_login_ip', 'last_login_device', 'two_factor_enabled'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('newsletter_subscribed', 'marketing_emails'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['verify_users', 'unverify_users', 'activate_users', 'deactivate_users']
    
    def get_queryset(self, request):
        """Filter users based on permissions"""
        qs = super().get_queryset(request)
        if request.user.is_superuser or (hasattr(request.user, 'is_master_admin') and request.user.is_master_admin()):
            return qs
        # Business owners see only their users
        if hasattr(request.user, 'business_profile'):
            return qs.filter(tenant=request.user.business_profile.tenant)
        return qs.none()
    
    def user_type_badge(self, obj):
        """Display user type with color"""
        colors = {
            'customer': '#3b82f6',
            'business_owner': '#f59e0b',
            'driver': '#10b981',
            'staff': '#8b5cf6',
            'master_admin': '#ef4444',
        }
        color = colors.get(obj.user_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_user_type_display()
        )
    user_type_badge.short_description = 'User Type'
    
    def tenant_name(self, obj):
        """Display tenant name"""
        return obj.tenant.name if obj.tenant else '—'
    tenant_name.short_description = 'Tenant/Business'
    
    def verified_badge(self, obj):
        """Display verification status"""
        if obj.is_verified:
            return format_html('<span style="color: #10b981; font-weight: bold;">✓ Verified</span>')
        return format_html('<span style="color: #ef4444;">✗ Not Verified</span>')
    verified_badge.short_description = 'Verification'
    
    def verify_users(self, request, queryset):
        """Action to verify users"""
        updated = queryset.update(is_verified=True, email_verified=True)
        self.message_user(request, f'{updated} user(s) verified.')
    verify_users.short_description = "✓ Mark selected users as verified"
    
    def unverify_users(self, request, queryset):
        """Action to unverify users"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} user(s) unverified.')
    unverify_users.short_description = "✗ Mark selected users as unverified"
    
    def activate_users(self, request, queryset):
        """Action to activate users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')
    activate_users.short_description = "▶ Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Action to deactivate users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    deactivate_users.short_description = "⏸ Deactivate selected users"


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Admin for customer profiles"""
    
    list_display = [
        'get_customer_name', 'tenant', 'loyalty_tier_badge', 'total_spent',
        'total_orders', 'average_rating', 'is_active', 'is_blocked'
    ]
    
    list_filter = [
        'loyalty_tier', 'is_active', 'is_blocked', 'tenant', 'created_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'user__phone_number',
        'user__registration_id', 'tenant__name'
    ]
    
    readonly_fields = [
        'user', 'total_spent', 'total_orders', 'average_rating', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('User & Tenant', {
            'fields': ('user', 'tenant')
        }),
        ('Loyalty & Rewards', {
            'fields': ('loyalty_points', 'loyalty_tier', 'total_spent', 'total_orders')
        }),
        ('Preferences', {
            'fields': ('preferred_delivery_address', 'preferred_payment_method')
        }),
        ('Ratings & Reviews', {
            'fields': ('average_rating', 'total_reviews')
        }),
        ('Account Status', {
            'fields': ('is_active', 'is_blocked', 'blocked_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_customer_name(self, obj):
        """Display customer full name"""
        return obj.user.get_full_name() or obj.user.username
    get_customer_name.short_description = 'Customer'
    
    def loyalty_tier_badge(self, obj):
        """Display loyalty tier with color"""
        colors = {
            'bronze': '#a16207',
            'silver': '#6b7280',
            'gold': '#d97706',
            'platinum': '#3b82f6',
        }
        color = colors.get(obj.loyalty_tier, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_loyalty_tier_display()
        )
    loyalty_tier_badge.short_description = 'Loyalty Tier'


@admin.register(BusinessOwnerProfile)
class BusinessOwnerProfileAdmin(admin.ModelAdmin):
    """Admin for business owner profiles with verification controls"""
    
    list_display = [
        'get_owner_name', 'tenant', 'approval_badge', 'id_verified',
        'total_revenue_display', 'total_orders_processed', 'average_rating',
        'is_suspended_badge'
    ]
    
    list_filter = [
        'is_approved', 'is_suspended', 'bank_account_verified', 'created_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'user__registration_id',
        'tenant__name', 'id_document_number'
    ]
    
    readonly_fields = [
        'user', 'tenant', 'total_revenue', 'total_orders_processed',
        'average_customer_rating', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('User & Business', {
            'fields': ('user', 'tenant')
        }),
        ('Identity Verification', {
            'fields': (
                'id_document_type', 'id_document_number', 'id_document_image'
            )
        }),
        ('Bank Account', {
            'fields': ('bank_account_verified',),
            'classes': ('collapse',)
        }),
        ('Business Metrics', {
            'fields': (
                'total_revenue', 'total_orders_processed',
                'average_customer_rating'
            ),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': (
                'can_create_staff', 'can_create_drivers', 'can_modify_commission'
            )
        }),
        ('Notifications', {
            'fields': ('notification_email', 'notification_phone'),
            'classes': ('collapse',)
        }),
        ('Account Status', {
            'fields': ('is_approved', 'is_suspended', 'suspension_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_owners', 'suspend_owners', 'unsuspend_owners']
    
    def get_owner_name(self, obj):
        """Display owner full name"""
        return obj.user.get_full_name() or obj.user.username
    get_owner_name.short_description = 'Owner'
    
    def approval_badge(self, obj):
        """Display approval status"""
        if obj.is_approved:
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 3px;">✓ Approved</span>'
            )
        return format_html(
            '<span style="background-color: #f59e0b; color: white; padding: 3px 8px; border-radius: 3px;">⏳ Pending</span>'
        )
    approval_badge.short_description = 'Approval'
    
    def id_verified(self, obj):
        """Display if ID is verified"""
        if obj.id_document_image:
            return format_html('<span style="color: #10b981;">✓ Uploaded</span>')
        return format_html('<span style="color: #ef4444;">✗ Not Uploaded</span>')
    id_verified.short_description = 'ID Document'
    
    def total_revenue_display(self, obj):
        """Display total revenue"""
        return f"${float(obj.total_revenue):,.2f}"
    total_revenue_display.short_description = 'Revenue'
    
    def is_suspended_badge(self, obj):
        """Display suspension status"""
        if obj.is_suspended:
            return format_html(
                '<span style="background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 3px;">⏸ Suspended</span>'
            )
        return format_html(
            '<span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 3px;">✓ Active</span>'
        )
    is_suspended_badge.short_description = 'Status'
    
    def approve_owners(self, request, queryset):
        """Action to approve owners"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} owner(s) approved.')
    approve_owners.short_description = "✓ Approve selected owners"
    
    def suspend_owners(self, request, queryset):
        """Action to suspend owners"""
        updated = queryset.update(is_suspended=True)
        self.message_user(request, f'{updated} owner(s) suspended.')
    suspend_owners.short_description = "⏸ Suspend selected owners"
    
    def unsuspend_owners(self, request, queryset):
        """Action to unsuspend owners"""
        updated = queryset.update(is_suspended=False)
        self.message_user(request, f'{updated} owner(s) unsuspended.')
    unsuspend_owners.short_description = "▶ Unsuspend selected owners"


@admin.register(UserLoginHistory)
class UserLoginHistoryAdmin(admin.ModelAdmin):
    """Track user login activity"""
    
    list_display = [
        'get_username', 'ip_address', 'device_info', 'login_time', 'logout_time'
    ]
    
    list_filter = ['login_time', 'browser']
    
    search_fields = ['user__username', 'user__email', 'ip_address']
    
    readonly_fields = ['user', 'login_time', 'logout_time', 'ip_address', 'device_info']
    
    def get_username(self, obj):
        """Display username"""
        return obj.user.username
    get_username.short_description = 'User'


@admin.register(UserNotificationPreferences)
class UserNotificationPreferencesAdmin(admin.ModelAdmin):
    """Admin for user notification preferences"""
    
    list_display = ['get_username', 'notify_count', 'channels_enabled']
    
    list_filter = [
        'email_notifications', 'sms_notifications', 'push_notifications',
        'notify_order_placed', 'notify_promotions'
    ]
    
    search_fields = ['user__username', 'user__email']
    
    readonly_fields = ['user', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Order Notifications', {
            'fields': (
                'notify_order_placed', 'notify_order_confirmed',
                'notify_order_shipped', 'notify_order_delivered'
            )
        }),
        ('Promotions & Marketing', {
            'fields': (
                'notify_promotions', 'notify_new_products', 'notify_special_offers'
            )
        }),
        ('Account & Security', {
            'fields': (
                'notify_account_changes', 'notify_security_alerts'
            )
        }),
        ('Delivery & Driver Notifications', {
            'fields': (
                'notify_delivery_requests', 'notify_delivery_updates'
            )
        }),
        ('Support & Issues', {
            'fields': (
                'notify_incident_updates', 'notify_support_responses'
            )
        }),
        ('Notification Channels', {
            'fields': (
                'email_notifications', 'sms_notifications',
                'push_notifications', 'in_app_notifications'
            )
        }),
        ('System', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_username(self, obj):
        """Display username"""
        return obj.user.username
    get_username.short_description = 'User'
    
    def notify_count(self, obj):
        """Count enabled notifications"""
        count = sum([
            obj.notify_order_placed, obj.notify_order_confirmed,
            obj.notify_order_shipped, obj.notify_order_delivered,
            obj.notify_promotions, obj.notify_new_products,
            obj.notify_special_offers, obj.notify_account_changes,
            obj.notify_security_alerts, obj.notify_delivery_requests,
            obj.notify_delivery_updates, obj.notify_incident_updates,
            obj.notify_support_responses
        ])
        return f"{count}/13 enabled"
    notify_count.short_description = 'Notifications'
    
    def channels_enabled(self, obj):
        """Show enabled channels"""
        channels = []
        if obj.email_notifications:
            channels.append('📧 Email')
        if obj.sms_notifications:
            channels.append('💬 SMS')
        if obj.push_notifications:
            channels.append('🔔 Push')
        if obj.in_app_notifications:
            channels.append('📱 In-App')
        return ', '.join(channels) if channels else 'None'
    channels_enabled.short_description = 'Channels'


# Register CustomUser with the custom admin
admin.site.unregister(CustomUser.__class__)
admin.site.register(CustomUser, CustomUserAdmin)
