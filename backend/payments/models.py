from django.db import models
from tenants.models import Tenant


class Payment(models.Model):
    PROVIDER_CHOICES = [
        # Card Payments
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('visa_mastercard', 'Visa/Mastercard'),
        
        # Digital Wallets - Global
        ('apple_pay', 'Apple Pay'),
        ('samsung_pay', 'Samsung Pay'),
        ('google_pay', 'Google Pay'),
        ('wallet', 'Digital Wallet'),
        
        # Local Payments (Bangladesh)
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        
        # Local Payments (Saudi Arabia / Arab Countries)
        ('mada', 'MADA (Saudi Arabia)'),
        ('stc_pay', 'STC Pay'),
        ('urpay', 'urPay'),
        
        # Others
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    payment_id = models.CharField(max_length=200, unique=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='SAR')
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.payment_id} ({self.provider})"

    def get_receipt(self):
        # Link to receipts app if available
        try:
            from receipts.models import Receipt as R
            return R.objects.filter(payment_id=self.payment_id).first()
        except Exception:
            return None


class Receipt(models.Model):
    payment_id = models.CharField(max_length=200)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    url = models.URLField(blank=True, null=True)
    invoice_no = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qr_code_url = models.URLField(blank=True, null=True)
    locale = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt {self.invoice_no} ({self.amount})"