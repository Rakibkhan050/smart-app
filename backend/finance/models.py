from django.db import models
from tenants.models import Tenant
from decimal import Decimal
from django.db.models import Sum, Q
from django.utils import timezone


class TaxRate(models.Model):
    """Tax rate configuration for different tax types."""
    TAX_TYPES = [
        ('vat', 'VAT'),
        ('sales', 'Sales Tax'),
        ('service', 'Service Tax'),
        ('other', 'Other'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    tax_type = models.CharField(max_length=20, choices=TAX_TYPES, default='vat')
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text='Tax rate as percentage (e.g., 15.00 for 15%)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tax Rate'
        verbose_name_plural = 'Tax Rates'

    def __str__(self):
        return f"{self.name} ({self.rate}%)"

    def calculate_tax(self, amount):
        """Calculate tax amount for a given base amount."""
        return (Decimal(amount) * self.rate / Decimal('100')).quantize(Decimal('0.01'))


class Expense(models.Model):
    """Track business expenses for P&L calculations."""
    EXPENSE_CATEGORIES = [
        ('cogs', 'Cost of Goods Sold'),
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('salaries', 'Salaries & Wages'),
        ('marketing', 'Marketing'),
        ('equipment', 'Equipment'),
        ('supplies', 'Supplies'),
        ('maintenance', 'Maintenance'),
        ('insurance', 'Insurance'),
        ('taxes', 'Taxes & Fees'),
        ('other', 'Other'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=50, choices=EXPENSE_CATEGORIES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.ForeignKey(TaxRate, on_delete=models.SET_NULL, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text='Amount + Tax')
    expense_date = models.DateField(help_text='Date when expense was incurred')
    paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        indexes = [
            models.Index(fields=['tenant', 'expense_date']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.category} - {self.amount} ({self.expense_date})"

    def save(self, *args, **kwargs):
        """Auto-calculate tax and total amount."""
        if self.tax_rate and self.amount:
            self.tax_amount = self.tax_rate.calculate_tax(self.amount)
        else:
            self.tax_amount = Decimal('0')
        self.total_amount = Decimal(self.amount) + Decimal(self.tax_amount)
        super().save(*args, **kwargs)


class ProfitLossReport(models.Model):
    """Cached P&L report snapshots for performance."""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Revenue
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Expenses by category
    cogs = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    operating_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Tax data
    total_tax_collected = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='VAT/tax collected from sales')
    total_tax_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Tax paid on expenses')
    net_tax_liability = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Calculations
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Profit & Loss Report'
        verbose_name_plural = 'Profit & Loss Reports'
        unique_together = [['tenant', 'start_date', 'end_date']]

    def __str__(self):
        return f"P&L {self.start_date} to {self.end_date} - Net: {self.net_profit}"

    @staticmethod
    def generate_report(tenant, start_date, end_date):
        """Generate P&L report for a date range."""
        from pos.models import Order
        
        # Calculate revenue from paid orders
        revenue_qs = Order.objects.filter(
            tenant=tenant,
            status='paid',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        total_revenue = revenue_qs.aggregate(total=Sum('total'))['total'] or Decimal('0')
        total_tax_collected = revenue_qs.aggregate(total=Sum('tax_amount'))['total'] or Decimal('0')
        
        # Calculate expenses
        expense_qs = Expense.objects.filter(
            tenant=tenant,
            expense_date__gte=start_date,
            expense_date__lte=end_date
        )
        cogs = expense_qs.filter(category='cogs').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        operating_expenses = expense_qs.exclude(category='cogs').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_tax_paid = expense_qs.aggregate(total=Sum('tax_amount'))['total'] or Decimal('0')
        
        # Calculate profits
        gross_profit = total_revenue - cogs
        net_profit = gross_profit - operating_expenses
        net_tax_liability = total_tax_collected - total_tax_paid
        
        # Create or update report
        report, created = ProfitLossReport.objects.update_or_create(
            tenant=tenant,
            start_date=start_date,
            end_date=end_date,
            defaults={
                'total_revenue': total_revenue,
                'cogs': cogs,
                'operating_expenses': operating_expenses,
                'total_tax_collected': total_tax_collected,
                'total_tax_paid': total_tax_paid,
                'net_tax_liability': net_tax_liability,
                'gross_profit': gross_profit,
                'net_profit': net_profit,
            }
        )
        
        return report
