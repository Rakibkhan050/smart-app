from django.db import models
from tenants.models import Tenant
from crm.models import Customer
from inventory.models import Product
from payments.models import Payment
from decimal import Decimal


class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('placed', 'Placed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

    def recalc_totals(self):
        items = self.items.all()
        subtotal = sum([Decimal(str(i.line_total())) for i in items])
        self.subtotal = subtotal
        # tax and shipping calculation may be tenant-specific; for now use stored values
        tax = Decimal(str(self.tax_amount or 0))
        shipping = Decimal(str(self.shipping_fee or 0))
        self.total = subtotal + tax + shipping
        self.save(update_fields=['subtotal', 'total'])

    def mark_paid(self, provider='visa_mastercard'):
        """Create a Payment, mark order paid, reduce product stock, and return the payment."""
        from django.db import transaction
        from payments.models import Payment
        with transaction.atomic():
            p = Payment.objects.create(payment_id=f'auto-{self.id}', tenant=self.tenant, provider=provider, status='completed', amount=self.total)
            self.payment = p
            self.status = 'paid'
            self.save(update_fields=['payment', 'status'])

            # decrement stock for products
            for item in self.items.select_related('product').all():
                prod = item.product
                try:
                    prod.quantity = max(Decimal(prod.quantity) - Decimal(item.quantity), Decimal('0'))
                    prod.save(update_fields=['quantity'])
                except Exception:
                    # best-effort; do not block payment
                    pass
        return p


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def line_total(self):
        try:
            return float(self.quantity) * float(self.unit_price)
        except Exception:
            return 0
