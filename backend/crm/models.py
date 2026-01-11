from django.db import models
from tenants.models import Tenant
from decimal import Decimal


class Customer(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True, db_index=True)
    phone = models.CharField(max_length=50, blank=True, db_index=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or (self.email or self.phone or 'Customer')

    def get_or_create_loyalty(self):
        """Get or create the loyalty points record for this customer."""
        loyalty, created = LoyaltyPoint.objects.get_or_create(customer=self)
        return loyalty


class LoyaltyPoint(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='loyalty')
    points = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer} - {self.points} pts"

    def add_points(self, amount, reason='', reference_order=None):
        """Add loyalty points and create a transaction record."""
        if amount <= 0:
            return None
        self.points += amount
        self.save(update_fields=['points', 'updated_at'])
        transaction = LoyaltyTransaction.objects.create(
            customer=self.customer,
            transaction_type='earn',
            points=amount,
            reason=reason,
            reference_order=reference_order
        )
        return transaction

    def redeem_points(self, amount, reason='', reference_order=None):
        """Redeem loyalty points and create a transaction record."""
        if amount <= 0 or self.points < amount:
            return None
        self.points -= amount
        self.save(update_fields=['points', 'updated_at'])
        transaction = LoyaltyTransaction.objects.create(
            customer=self.customer,
            transaction_type='redeem',
            points=-amount,
            reason=reason,
            reference_order=reference_order
        )
        return transaction


class LoyaltyTransaction(models.Model):
    """Track all loyalty point changes for audit trail."""
    TRANSACTION_TYPES = [
        ('earn', 'Earned'),
        ('redeem', 'Redeemed'),
        ('adjust', 'Adjustment'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loyalty_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()  # positive for earn, negative for redeem
    reason = models.CharField(max_length=255, blank=True)
    reference_order = models.ForeignKey('pos.Order', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Loyalty Transaction'
        verbose_name_plural = 'Loyalty Transactions'

    def __str__(self):
        sign = '+' if self.points > 0 else ''
        return f"{self.customer} {sign}{self.points} pts ({self.transaction_type})"


class PurchaseHistory(models.Model):
    """Link customers to their orders for easy purchase history tracking."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='purchases')
    order = models.OneToOneField('pos.Order', on_delete=models.CASCADE, related_name='purchase_record')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    loyalty_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Purchase History'
        verbose_name_plural = 'Purchase Histories'

    def __str__(self):
        return f"{self.customer} - Order #{self.order_id} - {self.amount}"

    @staticmethod
    def create_from_order(order):
        """Create purchase history record and accrue loyalty points when order is paid."""
        if not order.customer:
            return None
        
        # Calculate loyalty points (1 point per currency unit)
        loyalty_points = int(order.total)
        
        # Create purchase history
        purchase = PurchaseHistory.objects.create(
            customer=order.customer,
            order=order,
            amount=order.total,
            loyalty_earned=loyalty_points
        )
        
        # Accrue loyalty points
        loyalty = order.customer.get_or_create_loyalty()
        loyalty.add_points(
            amount=loyalty_points,
            reason=f'Purchase Order #{order.id}',
            reference_order=order
        )
        
        return purchase


class Supplier(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    payment_status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name