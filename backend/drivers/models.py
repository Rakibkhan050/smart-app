"""
Driver Management System for Multi-Business SaaS Platform
Tracks drivers, their assignments, and performance across all businesses
"""
from django.db import models
from django.contrib.auth import get_user_model
from tenants.models import Tenant
import uuid

User = get_user_model()


class DriverProfile(models.Model):
    """Driver Model - Can work for multiple businesses with verification"""
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('offline', 'Offline'),
        ('on_break', 'On Break'),
    ]
    
    VEHICLE_CHOICES = [
        ('bike', 'Bike/Motorcycle'),
        ('scooter', 'Scooter'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('truck', 'Truck'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    # IDs
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='driver_profile')
    
    # Basic Info
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, unique=True, db_index=True)
    email = models.EmailField(blank=True, db_index=True)
    registration_id = models.CharField(max_length=50, unique=True, db_index=True, help_text='Unique ID for global search')
    profile_picture = models.URLField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Assignment - Can work for multiple businesses
    assigned_businesses = models.ManyToManyField(
        Tenant,
        related_name='drivers',
        blank=True,
        help_text='Businesses this driver delivers for'
    )
    
    # Vehicle Info
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, default='bike')
    vehicle_number = models.CharField(max_length=50, blank=True)
    vehicle_registration_number = models.CharField(max_length=50, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    
    # Status & Location
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # ID & Document Verification (Business Owner Approval Required)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_drivers',
        limit_choices_to={'user_type': 'business_owner'}
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_rejection_reason = models.TextField(blank=True)
    
    # Performance Metrics
    total_deliveries = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    cancelled_deliveries = models.IntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        help_text='Out of 5.00'
    )
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_tips_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Account Status
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.TextField(blank=True)
    
    # Banking & Payouts
    bank_account_verified = models.BooleanField(default=False)
    last_payout_date = models.DateField(null=True, blank=True)
    pending_payout_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Driver Profile'
        verbose_name_plural = 'Driver Profiles'
        indexes = [
            models.Index(fields=['registration_id']),
            models.Index(fields=['phone']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.registration_id = f"DRV-{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def success_rate(self):
        """Calculate delivery success rate"""
        if self.total_deliveries == 0:
            return 0
        return (self.successful_deliveries / self.total_deliveries) * 100
    
    def approve_verification(self, verified_by_user):
        """Approve driver - Only by business owner"""
        from django.utils import timezone
        self.verification_status = 'approved'
        self.verified_by = verified_by_user
        self.verified_at = timezone.now()
        self.is_active = True
        self.save(update_fields=['verification_status', 'verified_by', 'verified_at', 'is_active'])
    
    def reject_verification(self, reason, verified_by_user):
        """Reject driver verification"""
        self.verification_status = 'rejected'
        self.verified_by = verified_by_user
        self.verification_rejection_reason = reason
        self.save(update_fields=['verification_status', 'verified_by', 'verification_rejection_reason'])


class DriverDocument(models.Model):
    """Store driver identification and verification documents"""
    
    DOCUMENT_TYPES = [
        ('national_id', 'National ID'),
        ('passport', 'Passport'),
        ('driver_license', 'Driver License'),
        ('vehicle_registration', 'Vehicle Registration'),
        ('insurance_document', 'Insurance Document'),
        ('police_clearance', 'Police Clearance'),
        ('other', 'Other'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='documents')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    
    # Document Details
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=100, blank=True)
    document_image_url = models.URLField()
    document_back_image_url = models.URLField(blank=True, help_text='Back side of document if applicable')
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents',
        limit_choices_to={'user_type': 'business_owner'}
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Expiry
    expiry_date = models.DateField(null=True, blank=True)
    
    # Upload Info
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        unique_together = ('driver', 'document_type')
    
    def __str__(self):
        return f"{self.driver.get_full_name()} - {self.get_document_type_display()}"
    
    def is_expired(self):
        """Check if document has expired"""
        if not self.expiry_date:
            return False
        from django.utils import timezone
        return self.expiry_date <= timezone.now().date()
    
    def verify_document(self, verified_by_user):
        """Verify the document"""
        from django.utils import timezone
        self.verification_status = 'verified'
        self.verified_by = verified_by_user
        self.verified_at = timezone.now()
        self.save(update_fields=['verification_status', 'verified_by', 'verified_at'])
    
    def reject_document(self, reason, verified_by_user):
        """Reject document verification"""
        self.verification_status = 'rejected'
        self.verified_by = verified_by_user
        self.rejection_reason = reason
        self.save(update_fields=['verification_status', 'verified_by', 'rejection_reason'])


class DriverAssignment(models.Model):
    """Track driver assignments to deliveries"""
    
    ASSIGNMENT_STATUS = [
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted'),
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='assignments')
    delivery = models.ForeignKey('delivery.Delivery', on_delete=models.CASCADE, related_name='driver_assignments')
    business = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    
    # Assignment Details
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True, help_text='When driver started delivery')
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS, default='assigned')
    is_completed = models.BooleanField(default=False)
    
    # Compensation
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    tip_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    bonus_earned = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='Bonus if completed early/efficiently')
    total_earnings = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Feedback & Rating
    customer_rating = models.IntegerField(null=True, blank=True, help_text='1-5 stars')
    customer_feedback = models.TextField(blank=True)
    driver_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['driver', 'status']),
            models.Index(fields=['business', 'assigned_at']),
        ]
    
    def __str__(self):
        return f"{self.driver.get_full_name()} → Delivery #{self.delivery.id}"
    
    def accept_delivery(self):
        """Driver accepts the delivery assignment"""
        from django.utils import timezone
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.driver.status = 'busy'
        self.driver.save(update_fields=['status'])
        self.save(update_fields=['status', 'accepted_at'])
    
    def start_delivery(self):
        """Driver starts the delivery"""
        from django.utils import timezone
        self.status = 'started'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def complete_delivery(self, tip=0):
        """Mark delivery as completed"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.is_completed = True
        self.tip_amount = tip
        self.total_earnings = self.delivery_fee + self.bonus_earned + tip
        
        # Update driver stats
        self.driver.total_deliveries += 1
        self.driver.successful_deliveries += 1
        self.driver.total_earnings += self.total_earnings
        self.driver.status = 'available'
        self.driver.save(update_fields=['total_deliveries', 'successful_deliveries', 'total_earnings', 'status'])
        
        self.save(update_fields=['status', 'completed_at', 'is_completed', 'tip_amount', 'total_earnings'])


class DriverEarnings(models.Model):
    """Track driver earnings and payout history"""
    
    PAYOUT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='earnings')
    
    # Earning Details
    earning_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, blank=True, help_text='Delivery ID or reference')
    
    # Payout
    payout_status = models.CharField(max_length=20, choices=PAYOUT_STATUS, default='pending')
    payout_date = models.DateField(null=True, blank=True)
    payout_reference = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-earning_date']
        indexes = [
            models.Index(fields=['driver', 'earning_date']),
        ]
    
    def __str__(self):
        return f"{self.driver.get_full_name()} - {self.amount} ({self.payout_status})"

