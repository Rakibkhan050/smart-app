from django.db import models


class Receipt(models.Model):
    payment_id = models.CharField(max_length=255)
    tenant_id = models.CharField(max_length=255)  # simple tenant FK placeholder
    invoice_number = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='SAR')
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    s3_key = models.CharField(max_length=500, blank=True, null=True)
    s3_url = models.URLField(blank=True, null=True)
    qr_code_url = models.URLField(blank=True, null=True)
    locale = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_presigned_url(self, expires_in=3600):
        # helper to generate presigned URL for s3_key if available
        if self.s3_key and hasattr(self, 's3_key'):
            try:
                import boto3
                from django.conf import settings
                s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                  endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                                  region_name=settings.AWS_S3_REGION_NAME)
                return s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': self.s3_key}, ExpiresIn=expires_in)
            except Exception:
                return None
        # fallback: return stored s3_url or None
        return self.s3_url

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number
