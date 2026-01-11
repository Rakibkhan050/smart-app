from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import (
    IncidentCategory, Incident, IncidentComment, IncidentFeedback, IncidentReport
)


class IncidentCommentInline(admin.TabularInline):
    """Inline editing of incident comments"""
    model = IncidentComment
    extra = 0
    readonly_fields = ['created_at', 'author']
    fields = ['author', 'message', 'is_internal', 'is_visible_to_customer', 'created_at']


class IncidentFeedbackInline(admin.StackedInline):
    """Inline display of incident feedback"""
    model = IncidentFeedback
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(IncidentCategory)
class IncidentCategoryAdmin(admin.ModelAdmin):
    """Admin for incident categories"""
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    """Admin for managing customer incidents and issues"""
    
    list_display = [
        'incident_id_display', 'title_short', 'reporter_display', 'tenant',
        'priority_badge', 'status_badge', 'days_open', 'assigned_to', 'incident_date'
    ]
    
    list_filter = [
        'status', 'priority', 'tenant', 'category', 'created_at', 'is_public'
    ]
    
    search_fields = [
        'id', 'title', 'description', 'reporter__username',
        'reporter__email', 'reporter__phone_number', 'tenant__name'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'acknowledged_at', 'resolved_at', 'closed_at',
        'updated_at', 'days_open_display', 'resolution_summary'
    ]
    
    fieldsets = (
        ('Incident Information', {
            'fields': ('id', 'tenant', 'title', 'description', 'category', 'incident_date')
        }),
        ('Reporter & Contact', {
            'fields': ('reporter',)
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'is_public')
        }),
        ('Assignment & Handling', {
            'fields': ('assigned_to',)
        }),
        ('Timeline', {
            'fields': (
                'created_at', 'acknowledged_at', 'resolved_at', 'closed_at',
                'days_open_display'
            ),
            'classes': ('collapse',)
        }),
        ('Resolution', {
            'fields': (
                'resolution_notes', 'resolution_action_taken',
                'compensation_offered', 'resolution_summary'
            )
        }),
        ('Attachments', {
            'fields': ('attachment_urls',),
            'classes': ('collapse',)
        }),
        ('Notifications', {
            'fields': ('notify_customer',),
            'classes': ('collapse',)
        })
    )
    
    inlines = [IncidentCommentInline, IncidentFeedbackInline]
    
    actions = [
        'acknowledge_incidents', 'start_investigation', 'resolve_incidents',
        'close_incidents', 'set_priority_critical', 'set_priority_low'
    ]
    
    def get_queryset(self, request):
        """Business owners see only their tenant's incidents"""
        qs = super().get_queryset(request)
        if request.user.is_superuser or (hasattr(request.user, 'is_master_admin') and request.user.is_master_admin()):
            return qs
        # Business owners see only their incidents
        if hasattr(request.user, 'business_profile'):
            return qs.filter(tenant=request.user.business_profile.tenant)
        return qs.none()
    
    def incident_id_display(self, obj):
        """Display incident ID"""
        return str(obj.id)[:8]
    incident_id_display.short_description = 'ID'
    
    def title_short(self, obj):
        """Display title (truncated)"""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'
    
    def reporter_display(self, obj):
        """Display reporter name"""
        return obj.reporter.get_full_name() or obj.reporter.username
    reporter_display.short_description = 'Reporter'
    
    def priority_badge(self, obj):
        """Display priority with color"""
        colors = {
            'critical': '#ef4444',
            'high': '#f59e0b',
            'medium': '#3b82f6',
            'low': '#10b981',
        }
        color = colors.get(obj.priority, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        """Display status with color"""
        colors = {
            'open': '#ef4444',
            'acknowledged': '#f59e0b',
            'investigating': '#3b82f6',
            'resolved': '#10b981',
            'closed': '#6b7280',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def days_open(self, obj):
        """Display days open"""
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        days = delta.days
        if days > 7:
            color = '#ef4444'
        elif days > 3:
            color = '#f59e0b'
        else:
            color = '#10b981'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} days</span>',
            color,
            days
        )
    days_open.short_description = 'Open For'
    
    def days_open_display(self, obj):
        """Display days open (for form)"""
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        return f"{delta.days} days, {delta.seconds // 3600} hours"
    days_open_display.short_description = 'Days Open'
    
    def resolution_summary(self, obj):
        """Display resolution summary"""
        if obj.status == 'resolved':
            return format_html(
                '''
                <div style="background: #f0fdf4; padding: 15px; border-radius: 8px; border: 2px solid #10b981;">
                    <h4 style="margin-top: 0; color: #10b981;">✓ Issue Resolved</h4>
                    <p><strong>Action Taken:</strong> {}</p>
                    <p><strong>Compensation:</strong> {} {}</p>
                    <p><strong>Notes:</strong> {}</p>
                </div>
                ''',
                obj.resolution_action_taken or '—',
                '$' if obj.compensation_offered else '—',
                f"{obj.compensation_offered:.2f}" if obj.compensation_offered else '',
                obj.resolution_notes or '—'
            )
        return format_html(
            '<div style="background: #fef3c7; padding: 15px; border-radius: 8px; color: #92400e;">No resolution yet</div>'
        )
    resolution_summary.short_description = 'Resolution Summary'
    
    def acknowledge_incidents(self, request, queryset):
        """Action to acknowledge incidents"""
        updated = 0
        for incident in queryset:
            if incident.status == 'open':
                incident.acknowledge(assigned_to=request.user)
                updated += 1
        self.message_user(request, f'{updated} incident(s) acknowledged.')
    acknowledge_incidents.short_description = "👁 Acknowledge selected incidents"
    
    def start_investigation(self, request, queryset):
        """Action to start investigation"""
        updated = queryset.filter(status__in=['open', 'acknowledged']).update(status='investigating')
        self.message_user(request, f'{updated} incident(s) marked as investigating.')
    start_investigation.short_description = "🔍 Start investigation"
    
    def resolve_incidents(self, request, queryset):
        """Action to mark as resolved"""
        for incident in queryset:
            if incident.status != 'resolved':
                incident.resolve('Resolved by admin')
        self.message_user(request, f'{queryset.count()} incident(s) marked as resolved.')
    resolve_incidents.short_description = "✓ Mark as resolved"
    
    def close_incidents(self, request, queryset):
        """Action to close incidents"""
        for incident in queryset:
            incident.close_incident()
        self.message_user(request, f'{queryset.count()} incident(s) closed.')
    close_incidents.short_description = "✓ Close selected incidents"
    
    def set_priority_critical(self, request, queryset):
        """Action to set priority to critical"""
        updated = queryset.update(priority='critical')
        self.message_user(request, f'{updated} incident(s) set to critical.')
    set_priority_critical.short_description = "🔴 Set priority to Critical"
    
    def set_priority_low(self, request, queryset):
        """Action to set priority to low"""
        updated = queryset.update(priority='low')
        self.message_user(request, f'{updated} incident(s) set to low.')
    set_priority_low.short_description = "🟢 Set priority to Low"


@admin.register(IncidentComment)
class IncidentCommentAdmin(admin.ModelAdmin):
    """Admin for incident comments"""
    
    list_display = [
        'incident_short', 'author', 'comment_preview', 'is_internal_badge',
        'is_visible_to_customer', 'created_at'
    ]
    
    list_filter = [
        'is_internal', 'is_visible_to_customer', 'created_at'
    ]
    
    search_fields = [
        'incident__title', 'author__username', 'message'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Comment Details', {
            'fields': ('incident', 'author', 'message')
        }),
        ('Visibility', {
            'fields': ('is_visible_to_customer', 'is_internal')
        }),
        ('Attachments', {
            'fields': ('attachment_urls',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def incident_short(self, obj):
        """Display incident title"""
        return obj.incident.title[:50]
    incident_short.short_description = 'Incident'
    
    def comment_preview(self, obj):
        """Preview comment (truncated)"""
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    comment_preview.short_description = 'Message'
    
    def is_internal_badge(self, obj):
        """Display if comment is internal"""
        if obj.is_internal:
            return format_html(
                '<span style="background-color: #6b7280; color: white; padding: 3px 8px; border-radius: 3px;">🔒 Internal</span>'
            )
        return format_html(
            '<span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 3px;">👤 Customer</span>'
        )
    is_internal_badge.short_description = 'Type'


@admin.register(IncidentFeedback)
class IncidentFeedbackAdmin(admin.ModelAdmin):
    """Admin for incident feedback"""
    
    list_display = [
        'incident_title', 'overall_rating_display', 'response_time_rating',
        'resolution_quality_rating', 'would_recommend_badge'
    ]
    
    list_filter = [
        'overall_satisfaction', 'response_time_rating', 'resolution_quality_rating',
        'would_recommend'
    ]
    
    search_fields = ['incident__title', 'positive_feedback', 'negative_feedback']
    
    readonly_fields = ['incident', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Incident', {
            'fields': ('incident',)
        }),
        ('Ratings', {
            'fields': (
                'overall_satisfaction', 'response_time_rating', 'resolution_quality_rating'
            )
        }),
        ('Feedback', {
            'fields': (
                'positive_feedback', 'negative_feedback', 'additional_comments'
            )
        }),
        ('Recommendation', {
            'fields': ('would_recommend',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def incident_title(self, obj):
        """Display incident title"""
        return obj.incident.title
    incident_title.short_description = 'Incident'
    
    def overall_rating_display(self, obj):
        """Display overall rating with stars"""
        stars = '⭐' * obj.overall_satisfaction
        return format_html(
            '<span style="font-weight: bold;">{}/5 {}</span>',
            obj.overall_satisfaction,
            stars
        )
    overall_rating_display.short_description = 'Overall Rating'


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    """Admin for incident reports and analytics"""
    
    list_display = [
        'report_id_short', 'tenant_display', 'report_type', 'date_range',
        'total_incidents', 'resolution_rate', 'average_satisfaction', 'generated_by'
    ]
    
    list_filter = [
        'report_type', 'start_date', 'end_date', 'tenant'
    ]
    
    search_fields = ['tenant__name', 'generated_by__username']
    
    readonly_fields = [
        'id', 'start_date', 'end_date', 'created_at', 'report_summary'
    ]
    
    fieldsets = (
        ('Report Information', {
            'fields': ('id', 'tenant', 'report_type', 'generated_by', 'created_at')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Incident Statistics', {
            'fields': (
                'total_incidents', 'open_incidents', 'resolved_incidents',
                'average_resolution_time'
            )
        }),
        ('By Priority', {
            'fields': (
                'critical_count', 'high_count', 'medium_count', 'low_count'
            ),
            'classes': ('collapse',)
        }),
        ('Satisfaction', {
            'fields': ('average_satisfaction_rating',)
        }),
        ('Category Breakdown', {
            'fields': ('category_breakdown',),
            'classes': ('collapse',)
        }),
        ('Summary & Notes', {
            'fields': ('summary', 'report_summary')
        })
    )
    
    def report_id_short(self, obj):
        """Display report ID"""
        return str(obj.id)[:8]
    report_id_short.short_description = 'Report ID'
    
    def tenant_display(self, obj):
        """Display tenant"""
        return obj.tenant.name if obj.tenant else 'Global'
    tenant_display.short_description = 'Tenant'
    
    def date_range(self, obj):
        """Display date range"""
        return f"{obj.start_date} to {obj.end_date}"
    date_range.short_description = 'Period'
    
    def resolution_rate(self, obj):
        """Display resolution rate"""
        if obj.total_incidents == 0:
            return '—'
        rate = (obj.resolved_incidents / obj.total_incidents) * 100
        return format_html(
            '<span style="color: #10b981; font-weight: bold;">{:.1f}%</span>',
            rate
        )
    resolution_rate.short_description = 'Resolution Rate'
    
    def average_satisfaction(self, obj):
        """Display average satisfaction"""
        rating = obj.average_satisfaction_rating
        color = '#10b981' if rating >= 4 else '#f59e0b' if rating >= 3 else '#ef4444'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}/5 ⭐</span>',
            color,
            rating
        )
    average_satisfaction.short_description = 'Avg. Satisfaction'
    
    def report_summary(self, obj):
        """Display report summary"""
        resolution_rate = (obj.resolved_incidents / obj.total_incidents * 100) if obj.total_incidents > 0 else 0
        return format_html(
            '''
            <div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">
                <h4 style="margin-top: 0;">Report Summary</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px;"><strong>Total Incidents:</strong></td>
                        <td style="padding: 5px; text-align: right;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Resolved:</strong></td>
                        <td style="padding: 5px; text-align: right; color: #10b981;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Still Open:</strong></td>
                        <td style="padding: 5px; text-align: right; color: #ef4444;">{}</td>
                    </tr>
                    <tr style="border-top: 2px solid #d1d5db;">
                        <td style="padding: 5px;"><strong>Resolution Rate:</strong></td>
                        <td style="padding: 5px; text-align: right; font-weight: bold;">{:.1f}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Avg. Resolution Time:</strong></td>
                        <td style="padding: 5px; text-align: right;">{} hours</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Customer Satisfaction:</strong></td>
                        <td style="padding: 5px; text-align: right;">{:.2f}/5 ⭐</td>
                    </tr>
                </table>
                <p style="margin-bottom: 0; color: #6b7280; font-size: 13px;">{}</p>
            </div>
            ''',
            obj.total_incidents,
            obj.resolved_incidents,
            obj.open_incidents,
            resolution_rate,
            obj.average_resolution_time,
            obj.average_satisfaction_rating,
            obj.summary or 'No additional notes.'
        )
    report_summary.short_description = 'Summary'
