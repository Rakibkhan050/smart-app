from django.db import models
from tenants.models import Tenant


class DeliveryPersonnel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Address(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    label = models.CharField(max_length=255, blank=True)
    line1 = models.CharField(max_length=255, blank=True)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    zone = models.CharField(max_length=50, blank=True, help_text='Zone/District for shipping fee calculation')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.label or self.line1 or 'Address'}"


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    order_reference = models.CharField(max_length=200, db_index=True)
    tracking_number = models.CharField(max_length=200, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_person = models.ForeignKey(DeliveryPersonnel, null=True, blank=True, on_delete=models.SET_NULL)
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expected_delivery = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery {self.tracking_number or self.order_reference} ({self.status})"

    def assign(self, delivery_person):
        """Assign a delivery person and update status."""
        self.delivery_person = delivery_person
        self.status = 'assigned'
        self.save()

    def mark_picked_up(self):
        """Mark as picked up."""
        self.status = 'picked_up'
        self.save()

    def mark_in_transit(self):
        """Mark as in transit."""
        self.status = 'in_transit'
        self.save()

    def mark_delivered(self):
        """Mark as delivered."""
        self.status = 'delivered'
        self.save()

    def mark_failed(self):
        """Mark as failed."""
        self.status = 'failed'
        self.save()


class ShippingFeeRule(models.Model):
    """Define shipping fee rules per tenant/zone."""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    zone = models.CharField(max_length=50, db_index=True, help_text='Zone/District name (e.g., "Downtown", "Suburbs")')
    base_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_km_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Additional fee per kilometer')
    min_distance = models.IntegerField(default=0, help_text='Minimum distance (km) for this rule')
    max_distance = models.IntegerField(default=1000, help_text='Maximum distance (km) for this rule')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['zone']
        unique_together = ('tenant', 'zone')

    def __str__(self):
        return f"{self.zone} - {self.base_fee} SAR"

    def calculate_fee(self, distance_km):
        """Calculate fee for given distance."""
        if distance_km < self.min_distance or distance_km > self.max_distance:
            return None
        return self.base_fee + (distance_km * self.per_km_fee)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'

    def __str__(self):
        return f"Delivery {self.order_reference} - {self.status}"
