from django.db import models
from django.utils.text import slugify
import uuid


class Tenant(models.Model):
    """Multi-Business SaaS Platform - Business/Store Model"""
    
    CATEGORY_CHOICES = [
        ('agriculture', 'Agriculture'),
        ('grocery', 'Grocery'),
        ('restaurant', 'Restaurant'),
        ('pharmacy', 'Pharmacy'),
        ('fashion', 'Fashion'),
        ('electronics', 'Electronics'),
        ('hardware', 'Hardware'),
        ('other', 'Other'),
    ]
    
    SUBSCRIPTION_TIERS = [
        ('basic', 'Basic - Single Store'),
        ('professional', 'Professional - Multiple Locations'),
        ('enterprise', 'Enterprise - Custom'),
    ]
    
    # Basic Info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text='Business/Store Name')
    slug = models.SlugField(unique=True)
    registration_id = models.CharField(max_length=50, unique=True, db_index=True, help_text='Unique registration ID for global search')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='agriculture')
    description = models.TextField(blank=True, help_text='Business description for storefront')
    
    # Branding & Visual Identity
    logo = models.URLField(blank=True, help_text='Business logo URL')
    banner_image = models.URLField(blank=True, help_text='Store banner/hero image URL')
    color_primary = models.CharField(max_length=7, default='#3B82F6', help_text='Primary brand color (hex)')
    color_secondary = models.CharField(max_length=7, default='#1F2937', help_text='Secondary brand color (hex)')
    
    # Privacy & Terms
    privacy_policy = models.TextField(blank=True, help_text='Custom privacy policy')
    terms_of_service = models.TextField(blank=True, help_text='Custom terms of service')
    return_policy = models.TextField(blank=True, help_text='Custom return/refund policy')
    
    # Contact Information
    owner_name = models.CharField(max_length=255, blank=True)
    owner_email = models.EmailField(blank=True, db_index=True)
    owner_phone = models.CharField(max_length=50, blank=True)
    business_phone = models.CharField(max_length=50, blank=True)
    business_address = models.TextField(blank=True)
    business_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    business_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Business Status & Verification
    is_active = models.BooleanField(default=True, help_text='Store is open for business')
    is_approved = models.BooleanField(default=False, help_text='Approved by master admin')
    verification_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')],
        default='pending'
    )
    business_registration_document = models.URLField(blank=True, help_text='Business registration document')
    tax_id = models.CharField(max_length=100, blank=True, help_text='Tax/VAT ID number')
    
    # Subscription & Plans
    subscription_tier = models.CharField(max_length=20, choices=SUBSCRIPTION_TIERS, default='basic')
    is_subscription_active = models.BooleanField(default=True)
    
    # Commission & Revenue
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.00,
        help_text='Platform commission percentage (set by master admin)'
    )
    total_sales = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        help_text='Lifetime sales for this business'
    )
    total_commission = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        help_text='Total commission earned by platform'
    )
    total_payouts = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        help_text='Total payouts to business owner'
    )
    
    # Settings & Configuration
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=5, default='en')
    operating_hours_enabled = models.BooleanField(default=False)
    
    # Analytics & Metrics
    total_customers = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps & Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Business/Tenant'
        verbose_name_plural = 'Businesses/Tenants'
        indexes = [
            models.Index(fields=['registration_id']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.registration_id:
            self.registration_id = f"REG-{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)
    
    def calculate_commission(self, order_amount):
        """Calculate commission for an order"""
        return (order_amount * self.commission_rate) / 100
    
    def get_storefront_url(self):
        """Get the unique storefront URL for this business"""
        return f"https://{self.slug}.storefront.local"


class TenantOperatingHours(models.Model):
    """Store operating hours for each business"""
    
    DAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='operating_hours')
    day_of_week = models.CharField(max_length=10, choices=DAYS)
    is_open = models.BooleanField(default=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('tenant', 'day_of_week')
        ordering = ['day_of_week']
    
    def __str__(self):
        status = f"{self.opening_time} - {self.closing_time}" if self.is_open else "Closed"
        return f"{self.get_day_of_week_display()}: {status}"


class TenantBankAccount(models.Model):
    """Bank account details for payouts"""
    
    ACCOUNT_TYPES = [
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('business', 'Business'),
    ]
    
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='bank_account')
    account_holder_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=255)
    bank_code = models.CharField(max_length=20, blank=True)
    iban = models.CharField(max_length=50, blank=True, help_text='International Bank Account Number')
    swift_code = models.CharField(max_length=20, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    is_verified = models.BooleanField(default=False, help_text='Verified by payment processor')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Tenant Bank Accounts'
    
    def __str__(self):
        return f"{self.tenant.name} - {self.account_holder_name}"
