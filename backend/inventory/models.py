from django.db import models
from tenants.models import Tenant
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    UNIT_PCS = 'pcs'
    UNIT_KG = 'kg'
    UNIT_LTR = 'ltr'
    UNIT_CHOICES = [
        (UNIT_PCS, _('Pieces')),
        (UNIT_KG, _('Kilogram')),
        (UNIT_LTR, _('Liter')),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True, db_index=True, help_text='Product category (e.g., Grocery, Electronics, Pharmacy)')
    sku = models.CharField(max_length=100, blank=True, db_index=True)
    barcode = models.CharField(max_length=200, blank=True, db_index=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=UNIT_PCS)

    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    low_stock_threshold = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.name} ({self.sku})" if self.sku else self.name

    @property
    def profit(self):
        try:
            return float(self.sell_price) - float(self.cost_price)
        except Exception:
            return 0

    def is_low_stock(self):
        try:
            return float(self.quantity) <= float(self.low_stock_threshold) and float(self.low_stock_threshold) > 0
        except Exception:
            return False
