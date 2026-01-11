from rest_framework import serializers
from .models import Expense, TaxRate, ProfitLossReport


class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = ['id', 'name', 'tax_type', 'rate', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExpenseSerializer(serializers.ModelSerializer):
    tax_rate_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Expense
        fields = [
            'id', 'category', 'description', 'amount', 'tax_rate', 'tax_rate_name',
            'tax_amount', 'total_amount', 'expense_date', 'paid', 'payment_date',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tax_amount', 'total_amount', 'created_at', 'updated_at']
    
    def get_tax_rate_name(self, obj):
        return str(obj.tax_rate) if obj.tax_rate else None


class ProfitLossReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfitLossReport
        fields = [
            'id', 'start_date', 'end_date', 'total_revenue', 'cogs', 'operating_expenses',
            'total_tax_collected', 'total_tax_paid', 'net_tax_liability',
            'gross_profit', 'net_profit', 'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']


class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics combining various data sources."""
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2)
    tax_liability = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Additional metrics
    total_orders = serializers.IntegerField()
    paid_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    
    # Expense breakdown
    expense_by_category = serializers.DictField()


class VATAggregationSerializer(serializers.Serializer):
    """Serializer for VAT/tax aggregation data."""
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    # VAT collected
    vat_on_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # VAT paid
    vat_on_purchases = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_purchases = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Net position
    net_vat_payable = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Breakdown by rate
    vat_by_rate = serializers.ListField(child=serializers.DictField())
