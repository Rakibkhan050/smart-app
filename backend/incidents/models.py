from django.db import models
from django.contrib.auth import get_user_model
from tenants.models import Tenant
import uuid

User = get_user_model()


class IncidentCategory(models.Model):
    """Categories for incident reporting"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Incident Categories'
    
    def __str__(self):
        return self.name


class Incident(models.Model):
    """Incident Reporting System - Customers can report issues directly to business owner"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Info
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='incidents')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    category = models.ForeignKey(IncidentCategory, on_delete=models.SET_NULL, null=True)
    
    # Details
    title = models.CharField(max_length=255)
    description = models.TextField()
    incident_date = models.DateTimeField()
    
    # Attachments (image/document URLs)
    attachment_urls = models.JSONField(default=list, blank=True, help_text='List of URLs for images/documents')
    
    # Status & Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Assignment & Resolution
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        limit_choices_to={'user_type__in': ['business_owner', 'staff']}
    )
    
    # Timeline
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    resolution_action_taken = models.TextField(blank=True)
    compensation_offered = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Refund/compensation amount if applicable'
    )
    
    # Visibility & Settings
    is_public = models.BooleanField(default=False, help_text='Visible to other customers?')
    notify_customer = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['reporter', 'created_at']),
        ]
    
    def __str__(self):
        return f"Incident #{self.id} - {self.title[:50]}"
    
    def acknowledge(self, assigned_to=None):
        """Mark incident as acknowledged"""
        from django.utils import timezone
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        if assigned_to:
            self.assigned_to = assigned_to
        self.save(update_fields=['status', 'acknowledged_at', 'assigned_to'])
    
    def start_investigation(self):
        """Change status to investigating"""
        self.status = 'investigating'
        self.save(update_fields=['status'])
    
    def resolve(self, resolution_notes, action_taken=''):
        """Mark incident as resolved"""
        from django.utils import timezone
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolution_notes = resolution_notes
        self.resolution_action_taken = action_taken
        self.save(update_fields=['status', 'resolved_at', 'resolution_notes', 'resolution_action_taken'])
    
    def close_incident(self):
        """Close the incident"""
        from django.utils import timezone
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at'])


class IncidentComment(models.Model):
    """Comments on incidents for communication between customer and business owner"""
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    
    # Visibility
    is_visible_to_customer = models.BooleanField(default=True)
    is_internal = models.BooleanField(default=False, help_text='Internal notes not visible to customer')
    
    # Attachments
    attachment_urls = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on Incident {self.incident.id}"


class IncidentFeedback(models.Model):
    """Customer feedback on incident resolution"""
    
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    incident = models.OneToOneField(Incident, on_delete=models.CASCADE, related_name='feedback')
    
    # Rating
    overall_satisfaction = models.IntegerField(choices=RATING_CHOICES, help_text='1-5 stars')
    response_time_rating = models.IntegerField(choices=RATING_CHOICES, help_text='How quickly was issue addressed?')
    resolution_quality_rating = models.IntegerField(choices=RATING_CHOICES, help_text='Quality of resolution?')
    
    # Feedback
    positive_feedback = models.TextField(blank=True, help_text='What went well?')
    negative_feedback = models.TextField(blank=True, help_text='What could be improved?')
    additional_comments = models.TextField(blank=True)
    
    # Would Recommend
    would_recommend = models.BooleanField(help_text='Would you recommend this business?')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Incident Feedbacks'
    
    def __str__(self):
        return f"Feedback for Incident {self.incident.id}"
    
    def average_rating(self):
        """Calculate average rating across all dimensions"""
        total = self.overall_satisfaction + self.response_time_rating + self.resolution_quality_rating
        return total / 3


class IncidentReport(models.Model):
    """Analytics reports for business owners and master admin"""
    
    REPORT_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Report Details
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='incident_reports', null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Date Range
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Statistics
    total_incidents = models.IntegerField(default=0)
    open_incidents = models.IntegerField(default=0)
    resolved_incidents = models.IntegerField(default=0)
    average_resolution_time = models.IntegerField(default=0, help_text='In hours')
    
    # By Priority
    critical_count = models.IntegerField(default=0)
    high_count = models.IntegerField(default=0)
    medium_count = models.IntegerField(default=0)
    low_count = models.IntegerField(default=0)
    
    # By Category
    category_breakdown = models.JSONField(default=dict, blank=True)
    
    # Satisfaction
    average_satisfaction_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        help_text='Average customer satisfaction (1-5)'
    )
    
    # Summary
    summary = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        tenant_name = self.tenant.name if self.tenant else 'Global'
        return f"{tenant_name} - {self.get_report_type_display()} Report ({self.start_date} to {self.end_date})"
