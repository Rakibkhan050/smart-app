from django.db import models


class Receipt(models.Model):
    payment_id = models.CharField(max_length=255)
    tenant_id = models.CharField(max_length=255)  # simple tenant FK placeholder
    invoice_number = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='SAR')
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    s3_url = models.URLField(blank=True, null=True)
    qr_code_url = models.URLField(blank=True, null=True)
    locale = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number
