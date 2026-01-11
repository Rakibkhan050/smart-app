from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from accounts.permissions import RolesAllowed
from .models import Expense, TaxRate, ProfitLossReport
from .serializers import (
    ExpenseSerializer, TaxRateSerializer, ProfitLossReportSerializer,
    DashboardMetricsSerializer, VATAggregationSerializer
)


class TaxRateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tax rates."""
    serializer_class = TaxRateSerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager']

    def get_queryset(self):
        user = self.request.user
        qs = TaxRate.objects.all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing expenses."""
    serializer_class = ExpenseSerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager']

    def get_queryset(self):
        user = self.request.user
        qs = Expense.objects.select_related('tax_rate').all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get expenses grouped by category."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        qs = self.get_queryset()
        
        if start_date:
            qs = qs.filter(expense_date__gte=start_date)
        if end_date:
            qs = qs.filter(expense_date__lte=end_date)
        
        category_totals = qs.values('category').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        return Response(category_totals)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark an expense as paid."""
        expense = self.get_object()
        expense.paid = True
        expense.payment_date = request.data.get('payment_date', timezone.now().date())
        expense.save(update_fields=['paid', 'payment_date'])
        
        serializer = self.get_serializer(expense)
        return Response(serializer.data)


class ReportViewSet(viewsets.ViewSet):
    """ViewSet for financial reports and analytics."""
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager']

    def get_tenant(self):
        user = self.request.user
        if user.is_superuser:
            return None
        return getattr(user, 'tenant', None)

    @action(detail=False, methods=['get'])
    def profit_loss(self, request):
        """Generate P&L report for a date range."""
        tenant = self.get_tenant()
        if tenant is None and not request.user.is_superuser:
            return Response(
                {'error': 'No tenant associated with user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            # Default to current month
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = today
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Generate report
        report = ProfitLossReport.generate_report(tenant, start_date, end_date)
        serializer = ProfitLossReportSerializer(report)
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def vat_aggregation(self, request):
        """Generate VAT aggregation report."""
        tenant = self.get_tenant()
        if tenant is None and not request.user.is_superuser:
            return Response(
                {'error': 'No tenant associated with user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            # Default to current month
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = today
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        from pos.models import Order
        
        # VAT on sales
        sales_qs = Order.objects.filter(
            tenant=tenant,
            status='paid',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        vat_on_sales = sales_qs.aggregate(total=Sum('tax_amount'))['total'] or Decimal('0')
        total_sales = sales_qs.aggregate(total=Sum('total'))['total'] or Decimal('0')
        
        # VAT on purchases/expenses
        expense_qs = Expense.objects.filter(
            tenant=tenant,
            expense_date__gte=start_date,
            expense_date__lte=end_date
        )
        vat_on_purchases = expense_qs.aggregate(total=Sum('tax_amount'))['total'] or Decimal('0')
        total_purchases = expense_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Net VAT position
        net_vat_payable = vat_on_sales - vat_on_purchases
        
        # VAT by rate
        vat_by_rate = []
        tax_rates = TaxRate.objects.filter(tenant=tenant, is_active=True)
        for rate in tax_rates:
            expenses_with_rate = expense_qs.filter(tax_rate=rate).aggregate(
                total=Sum('tax_amount')
            )['total'] or Decimal('0')
            
            vat_by_rate.append({
                'rate_name': rate.name,
                'rate_percentage': float(rate.rate),
                'tax_type': rate.tax_type,
                'amount': float(expenses_with_rate)
            })
        
        data = {
            'period_start': start_date,
            'period_end': end_date,
            'vat_on_sales': vat_on_sales,
            'total_sales': total_sales,
            'vat_on_purchases': vat_on_purchases,
            'total_purchases': total_purchases,
            'net_vat_payable': net_vat_payable,
            'vat_by_rate': vat_by_rate
        }
        
        serializer = VATAggregationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Generate dashboard metrics."""
        tenant = self.get_tenant()
        if tenant is None and not request.user.is_superuser:
            return Response(
                {'error': 'No tenant associated with user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Date range (default to last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        start_param = request.query_params.get('start_date')
        end_param = request.query_params.get('end_date')
        
        if start_param:
            start_date = datetime.strptime(start_param, '%Y-%m-%d').date()
        if end_param:
            end_date = datetime.strptime(end_param, '%Y-%m-%d').date()
        
        from pos.models import Order
        
        # Revenue metrics
        order_qs = Order.objects.filter(
            tenant=tenant,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        paid_orders = order_qs.filter(status='paid')
        total_revenue = paid_orders.aggregate(total=Sum('total'))['total'] or Decimal('0')
        tax_collected = paid_orders.aggregate(total=Sum('tax_amount'))['total'] or Decimal('0')
        
        # Expense metrics
        expense_qs = Expense.objects.filter(
            tenant=tenant,
            expense_date__gte=start_date,
            expense_date__lte=end_date
        )
        total_expenses = expense_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Calculate net profit and margin
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else Decimal('0')
        
        # Order counts
        total_orders = order_qs.count()
        paid_count = paid_orders.count()
        pending_count = order_qs.filter(Q(status='draft') | Q(status='placed')).count()
        
        # Expense by category
        expense_by_category = {}
        category_data = expense_qs.values('category').annotate(
            total=Sum('total_amount')
        )
        for item in category_data:
            expense_by_category[item['category']] = float(item['total'])
        
        data = {
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'profit_margin': profit_margin,
            'tax_liability': tax_collected,
            'total_orders': total_orders,
            'paid_orders': paid_count,
            'pending_orders': pending_count,
            'expense_by_category': expense_by_category
        }
        
        serializer = DashboardMetricsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)
