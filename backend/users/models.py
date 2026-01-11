from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from tenants.models import Tenant
import uuid


class CustomUser(AbstractUser):
    """Extended user model for multi-tenant support"""
    
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business_owner', 'Business Owner'),
        ('driver', 'Driver'),
        ('staff', 'Business Staff'),
        ('master_admin', 'Master Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    
    # Multi-tenant relationship
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    
    # Profile Information
    phone_number = models.CharField(max_length=50, blank=True, db_index=True)
    registration_id = models.CharField(max_length=50, unique=True, db_index=True, help_text='Unique ID for global search')
    profile_picture = models.URLField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        blank=True
    )
    bio = models.TextField(blank=True)
    
    # Address & Location
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Account Status & Verification
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True)
    phone_verification_token = models.CharField(max_length=255, blank=True)
    
    # Account Activity
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_device = models.CharField(max_length=255, blank=True)
    
    # Privacy & Preferences
    two_factor_enabled = models.BooleanField(default=False)
    newsletter_subscribed = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['registration_id']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['user_type']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_user_type_display()})"
    
    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.registration_id = f"USR-{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_customer(self):
        return self.user_type == 'customer'
    
    def is_business_owner(self):
        return self.user_type == 'business_owner'
    
    def is_driver(self):
        return self.user_type == 'driver'
    
    def is_staff_member(self):
        return self.user_type == 'staff'
    
    def is_master_admin(self):
        return self.user_type == 'master_admin'


class CustomerProfile(models.Model):
    """Extended profile for customer users"""
    
    LOYALTY_TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='customers')
    
    # Loyalty & Rewards
    loyalty_points = models.IntegerField(default=0)
    loyalty_tier = models.CharField(max_length=20, choices=LOYALTY_TIER_CHOICES, default='bronze')
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    
    # Preferences
    preferred_delivery_address = models.TextField(blank=True)
    preferred_payment_method = models.CharField(max_length=50, blank=True)
    
    # Analytics
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.tenant.name}"
    
    def upgrade_loyalty_tier(self):
        """Automatically upgrade loyalty tier based on total spent"""
        if self.total_spent >= 5000:
            self.loyalty_tier = 'platinum'
        elif self.total_spent >= 2000:
            self.loyalty_tier = 'gold'
        elif self.total_spent >= 500:
            self.loyalty_tier = 'silver'
        else:
            self.loyalty_tier = 'bronze'
        self.save(update_fields=['loyalty_tier'])


class BusinessOwnerProfile(models.Model):
    """Extended profile for business owner users"""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='business_profile')
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='owner_profile')
    
    # Identity Verification
    id_document_type = models.CharField(
        max_length=20,
        choices=[('passport', 'Passport'), ('national_id', 'National ID'), ('driver_license', 'Driver License')],
        blank=True
    )
    id_document_number = models.CharField(max_length=100, blank=True)
    id_document_image = models.URLField(blank=True)
    
    # Bank Details
    bank_account_verified = models.BooleanField(default=False)
    
    # Business Metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_orders_processed = models.IntegerField(default=0)
    average_customer_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    # Permissions & Features
    can_create_staff = models.BooleanField(default=True)
    can_create_drivers = models.BooleanField(default=True)
    can_modify_commission = models.BooleanField(default=False)
    
    # Settings
    notification_email = models.EmailField(blank=True)
    notification_phone = models.CharField(max_length=50, blank=True)
    
    # Status
    is_approved = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Business Owner Profile'
        verbose_name_plural = 'Business Owner Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.tenant.name} (Owner)"


class UserLoginHistory(models.Model):
    """Track login history for security and analytics"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    device_info = models.CharField(max_length=255, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class UserNotificationPreferences(models.Model):
    """User preferences for different types of notifications"""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Order Notifications
    notify_order_placed = models.BooleanField(default=True)
    notify_order_confirmed = models.BooleanField(default=True)
    notify_order_shipped = models.BooleanField(default=True)
    notify_order_delivered = models.BooleanField(default=True)
    
    # Promotion & Marketing
    notify_promotions = models.BooleanField(default=True)
    notify_new_products = models.BooleanField(default=False)
    notify_special_offers = models.BooleanField(default=True)
    
    # Account Notifications
    notify_account_changes = models.BooleanField(default=True)
    notify_security_alerts = models.BooleanField(default=True)
    
    # Delivery Notifications (for drivers/owners)
    notify_delivery_requests = models.BooleanField(default=True)
    notify_delivery_updates = models.BooleanField(default=True)
    
    # Incident & Support
    notify_incident_updates = models.BooleanField(default=True)
    notify_support_responses = models.BooleanField(default=True)
    
    # Channels
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
