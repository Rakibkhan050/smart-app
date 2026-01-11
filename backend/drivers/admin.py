from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import (
    DriverProfile, DriverDocument, DriverAssignment, DriverEarnings, LocationHistory
)


class DriverDocumentInline(admin.TabularInline):
    """Inline editing of driver documents"""
    model = DriverDocument
    extra = 0
    readonly_fields = ['uploaded_at']
    fields = [
        'document_type', 'document_number', 'verification_status',
        'expiry_date', 'uploaded_at'
    ]


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    """Admin for driver profiles with verification controls"""
    
    list_display = [
        'get_driver_name', 'registration_id', 'phone', 'status_badge',
        'verification_badge', 'total_deliveries', 'success_rate_display',
        'average_rating', 'total_earnings_display', 'created_at'
    ]
    
    list_filter = [
        'status', 'verification_status', 'is_active', 'is_blocked',
        'assigned_businesses', 'vehicle_type', 'created_at'
    ]
    
    search_fields = [
        'first_name', 'last_name', 'phone', 'email',
        'registration_id', 'license_number', 'vehicle_number'
    ]
    
    readonly_fields = [
        'id', 'registration_id', 'user', 'total_deliveries',
        'successful_deliveries', 'failed_deliveries', 'total_earnings',
        'created_at', 'updated_at', 'performance_summary'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'first_name', 'last_name', 'registration_id',
                      'phone', 'email', 'date_of_birth', 'profile_picture')
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_type', 'vehicle_number', 'vehicle_registration_number',
                      'license_number', 'license_expiry')
        }),
        ('Business Assignment', {
            'fields': ('assigned_businesses',)
        }),
        ('Status & Location', {
            'fields': ('status', 'current_latitude', 'current_longitude',
                      'last_location_update')
        }),
        ('ID & Document Verification', {
            'fields': ('verification_status', 'verified_by', 'verified_at',
                      'verification_rejection_reason'),
            'description': 'Business owner must approve drivers before they can deliver'
        }),
        ('Performance Metrics', {
            'fields': ('total_deliveries', 'successful_deliveries', 'failed_deliveries',
                      'cancelled_deliveries', 'average_rating', 'performance_summary'),
            'classes': ('collapse',)
        }),
        ('Financial', {
            'fields': ('total_earnings', 'total_tips_earned', 'bank_account_verified',
                      'last_payout_date', 'pending_payout_amount'),
            'classes': ('collapse',)
        }),
        ('Account Status', {
            'fields': ('is_active', 'is_blocked', 'block_reason')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [DriverDocumentInline]
    
    actions = ['approve_verification', 'reject_verification', 'activate_drivers',
              'deactivate_drivers', 'block_drivers', 'unblock_drivers']
    
    def get_queryset(self, request):
        """Master admin and business owners see relevant drivers"""
        qs = super().get_queryset(request)
        if request.user.is_superuser or (hasattr(request.user, 'is_master_admin') and request.user.is_master_admin()):
            return qs
        # Business owners see only their drivers
        if hasattr(request.user, 'business_profile'):
            return qs.filter(assigned_businesses=request.user.business_profile.tenant)
        return qs.none()
    
    def get_driver_name(self, obj):
        """Display driver full name"""
        return f"{obj.first_name} {obj.last_name}"
    get_driver_name.short_description = 'Driver Name'
    
    def status_badge(self, obj):
        """Display driver status"""
        colors = {
            'available': '#10b981',
            'busy': '#f59e0b',
            'offline': '#6b7280',
            'on_break': '#3b82f6',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def verification_badge(self, obj):
        """Display verification status"""
        colors = {
            'pending': '#f59e0b',
            'approved': '#10b981',
            'rejected': '#ef4444',
            'suspended': '#ef4444',
        }
        color = colors.get(obj.verification_status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_verification_status_display()
        )
    verification_badge.short_description = 'Verification'
    
    def success_rate_display(self, obj):
        """Display success rate"""
        rate = obj.success_rate
        if rate >= 95:
            color = '#10b981'
        elif rate >= 80:
            color = '#f59e0b'
        else:
            color = '#ef4444'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color,
            rate
        )
    success_rate_display.short_description = 'Success Rate'
    
    def total_earnings_display(self, obj):
        """Display total earnings"""
        return format_html(
            '<strong>${:,.2f}</strong>',
            obj.total_earnings
        )
    total_earnings_display.short_description = 'Earnings'
    
    def performance_summary(self, obj):
        """Display performance summary"""
        return format_html(
            '''
            <div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">
                <h4 style="margin-top: 0;">Performance Summary</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px;"><strong>Total Deliveries:</strong></td>
                        <td style="padding: 5px; text-align: right;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Successful:</strong></td>
                        <td style="padding: 5px; text-align: right; color: #10b981;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Failed:</strong></td>
                        <td style="padding: 5px; text-align: right; color: #ef4444;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Cancelled:</strong></td>
                        <td style="padding: 5px; text-align: right; color: #6b7280;">{}</td>
                    </tr>
                    <tr style="border-top: 2px solid #d1d5db;">
                        <td style="padding: 5px;"><strong>Avg. Rating:</strong></td>
                        <td style="padding: 5px; text-align: right; font-weight: bold;">{:.2f}/5.00 ⭐</td>
                    </tr>
                </table>
            </div>
            ''',
            obj.total_deliveries,
            obj.successful_deliveries,
            obj.failed_deliveries,
            obj.cancelled_deliveries,
            obj.average_rating
        )
    performance_summary.short_description = 'Performance'
    
    def approve_verification(self, request, queryset):
        """Action for business owner to approve driver"""
        updated = 0
        for driver in queryset:
            if driver.verification_status == 'pending':
                driver.approve_verification(request.user)
                updated += 1
        self.message_user(request, f'{updated} driver(s) approved.')
    approve_verification.short_description = "✓ Approve selected drivers"
    
    def reject_verification(self, request, queryset):
        """Action for business owner to reject driver"""
        for driver in queryset:
            driver.verification_status = 'rejected'
            driver.verified_by = request.user
            driver.save(update_fields=['verification_status', 'verified_by'])
        self.message_user(request, f'{queryset.count()} driver(s) rejected.')
    reject_verification.short_description = "✗ Reject selected drivers"
    
    def activate_drivers(self, request, queryset):
        """Action to activate drivers"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} driver(s) activated.')
    activate_drivers.short_description = "▶ Activate selected drivers"
    
    def deactivate_drivers(self, request, queryset):
        """Action to deactivate drivers"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} driver(s) deactivated.')
    deactivate_drivers.short_description = "⏸ Deactivate selected drivers"
    
    def block_drivers(self, request, queryset):
        """Action to block drivers"""
        updated = queryset.update(is_blocked=True)
        self.message_user(request, f'{updated} driver(s) blocked.')
    block_drivers.short_description = "🚫 Block selected drivers"
    
    def unblock_drivers(self, request, queryset):
        """Action to unblock drivers"""
        updated = queryset.update(is_blocked=False)
        self.message_user(request, f'{updated} driver(s) unblocked.')
    unblock_drivers.short_description = "✓ Unblock selected drivers"


@admin.register(DriverDocument)
class DriverDocumentAdmin(admin.ModelAdmin):
    """Admin for managing driver documents and verification"""
    
    list_display = [
        'get_driver_name', 'document_type', 'document_number',
        'verification_status_badge', 'expiry_status', 'verified_by', 'uploaded_at'
    ]
    
    list_filter = [
        'document_type', 'verification_status', 'expiry_date', 'tenant', 'uploaded_at'
    ]
    
    search_fields = [
        'driver__first_name', 'driver__last_name', 'driver__registration_id',
        'document_number'
    ]
    
    readonly_fields = [
        'id', 'driver', 'tenant', 'uploaded_at', 'updated_at',
        'document_preview'
    ]
    
    fieldsets = (
        ('Driver & Tenant', {
            'fields': ('id', 'driver', 'tenant')
        }),
        ('Document Details', {
            'fields': ('document_type', 'document_number', 'document_image_url',
                      'document_back_image_url', 'expiry_date')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verified_by', 'verified_at',
                      'rejection_reason')
        }),
        ('Preview', {
            'fields': ('document_preview',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['verify_documents', 'reject_documents']
    
    def get_driver_name(self, obj):
        """Display driver name"""
        return obj.driver.get_full_name()
    get_driver_name.short_description = 'Driver'
    
    def verification_status_badge(self, obj):
        """Display verification status"""
        colors = {
            'pending': '#f59e0b',
            'verified': '#10b981',
            'rejected': '#ef4444',
            'expired': '#ef4444',
        }
        color = colors.get(obj.verification_status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_verification_status_display()
        )
    verification_status_badge.short_description = 'Status'
    
    def expiry_status(self, obj):
        """Display expiry status"""
        if not obj.expiry_date:
            return '—'
        if obj.is_expired():
            return format_html('<span style="color: #ef4444; font-weight: bold;">🚫 Expired</span>')
        return format_html('<span style="color: #10b981;">✓ Valid</span>')
    expiry_status.short_description = 'Expiry'
    
    def document_preview(self, obj):
        """Preview document image"""
        if obj.document_image_url:
            return format_html(
                '<img src="{}" style="max-width: 300px; border-radius: 4px; margin-bottom: 10px;"/><br>',
                obj.document_image_url
            )
        return '—'
    document_preview.short_description = 'Document Image'
    
    def verify_documents(self, request, queryset):
        """Action to verify documents"""
        updated = 0
        for doc in queryset:
            if doc.verification_status == 'pending':
                doc.verify_document(request.user)
                updated += 1
        self.message_user(request, f'{updated} document(s) verified.')
    verify_documents.short_description = "✓ Verify selected documents"
    
    def reject_documents(self, request, queryset):
        """Action to reject documents"""
        for doc in queryset:
            doc.verification_status = 'rejected'
            doc.verified_by = request.user
            doc.save(update_fields=['verification_status', 'verified_by'])
        self.message_user(request, f'{queryset.count()} document(s) rejected.')
    reject_documents.short_description = "✗ Reject selected documents"


@admin.register(DriverAssignment)
class DriverAssignmentAdmin(admin.ModelAdmin):
    """Admin for tracking driver assignments"""
    
    list_display = [
        'id', 'get_driver_name', 'get_delivery_id', 'status_badge',
        'assigned_at', 'completed_at', 'total_earnings_display', 'customer_rating'
    ]
    
    list_filter = [
        'status', 'assigned_at', 'business', 'driver'
    ]
    
    search_fields = [
        'driver__first_name', 'driver__last_name', 'driver__phone',
        'delivery__order_reference', 'delivery__tracking_number'
    ]
    
    readonly_fields = [
        'id', 'driver', 'delivery', 'business', 'assigned_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('id', 'driver', 'delivery', 'business', 'status')
        }),
        ('Timeline', {
            'fields': ('assigned_at', 'accepted_at', 'started_at',
                      'completed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Compensation', {
            'fields': ('delivery_fee', 'tip_amount', 'bonus_earned', 'total_earnings')
        }),
        ('Feedback', {
            'fields': ('customer_rating', 'customer_feedback', 'driver_notes')
        })
    )
    
    def get_driver_name(self, obj):
        """Display driver name"""
        return obj.driver.get_full_name()
    get_driver_name.short_description = 'Driver'
    
    def get_delivery_id(self, obj):
        """Display delivery reference"""
        return obj.delivery.order_reference or f"#{obj.delivery.id}"
    get_delivery_id.short_description = 'Delivery'
    
    def status_badge(self, obj):
        """Display status"""
        colors = {
            'assigned': '#3b82f6',
            'accepted': '#8b5cf6',
            'started': '#f59e0b',
            'completed': '#10b981',
            'cancelled': '#ef4444',
            'failed': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def total_earnings_display(self, obj):
        """Display total earnings"""
        return format_html(
            '<strong>${:,.2f}</strong>',
            obj.total_earnings
        )
    total_earnings_display.short_description = 'Earnings'


@admin.register(DriverEarnings)
class DriverEarningsAdmin(admin.ModelAdmin):
    """Admin for tracking driver earnings and payouts"""
    
    list_display = [
        'get_driver_name', 'earning_date', 'amount_display',
        'payout_status_badge', 'payout_date', 'reference'
    ]
    
    list_filter = [
        'payout_status', 'earning_date', 'payout_date'
    ]
    
    search_fields = [
        'driver__first_name', 'driver__last_name', 'driver__registration_id',
        'reference', 'payout_reference'
    ]
    
    readonly_fields = [
        'id', 'driver', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Driver & Earning', {
            'fields': ('id', 'driver', 'earning_date', 'amount', 'description', 'reference')
        }),
        ('Payout', {
            'fields': ('payout_status', 'payout_date', 'payout_reference')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_driver_name(self, obj):
        """Display driver name"""
        return obj.driver.get_full_name()
    get_driver_name.short_description = 'Driver'
    
    def amount_display(self, obj):
        """Display amount"""
        return format_html(
            '<strong>${:,.2f}</strong>',
            obj.amount
        )
    amount_display.short_description = 'Amount'
    
    def payout_status_badge(self, obj):
        """Display payout status"""
        colors = {
            'pending': '#f59e0b',
            'processing': '#3b82f6',
            'paid': '#10b981',
            'failed': '#ef4444',
        }
        color = colors.get(obj.payout_status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_payout_status_display()
        )
    payout_status_badge.short_description = 'Payout Status'


@admin.register(LocationHistory)
class LocationHistoryAdmin(admin.ModelAdmin):
    """Admin for driver location tracking history"""
    list_display = [
        'driver', 'timestamp', 'location_display', 'speed', 
        'assignment', 'accuracy'
    ]
    list_filter = ['timestamp', 'driver']
    search_fields = ['driver__first_name', 'driver__last_name', 'driver__phone']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = [
        ('Location', {
            'fields': ('driver', 'assignment', 'latitude', 'longitude')
        }),
        ('Details', {
            'fields': ('accuracy', 'speed', 'heading', 'timestamp')
        }),
    ]
    
    def location_display(self, obj):
        """Display location coordinates"""
        return f"{obj.latitude}, {obj.longitude}"
    location_display.short_description = 'Coordinates'
