"""
Dashboard API for 3D visualization with Three.js
Aggregates financial, delivery, inventory, and automation metrics
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from finance.models import ProfitLossReport, Expense
from delivery.models import Delivery
from inventory.models import Product
from pos.models import Order, OrderItem
from payments.models import Payment
from notifications.models import Notification


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_3d_metrics(request):
    """
    Return comprehensive metrics for 3D dashboard visualization.
    
    Query Parameters:
    - days: Number of days to look back (default: 30)
    - start_date: Start date YYYY-MM-DD (optional)
    - end_date: End date YYYY-MM-DD (optional)
    
    Returns:
    {
        "financial": {
            "revenue_trend": [...],
            "expense_breakdown": [...],
            "profit_margin_trend": [...]
        },
        "delivery": {
            "status_distribution": [...],
            "delivery_map": [...],
            "completion_rate": ...
        },
        "inventory": {
            "low_stock_count": ...,
            "categories": [...],
            "restock_alerts": [...]
        },
        "automation": {
            "task_execution": [...],
            "notification_stats": {...}
        }
    }
    """
    # Get tenant from authenticated user
    tenant = None
    if hasattr(request.user, 'tenant'):
        tenant = request.user.tenant
        
    if not tenant:
        return Response({
            "error": "No tenant found. Please create a tenant first.",
            "date_range": {"start": "", "end": "", "days": 0},
            "financial": {
                "revenue_trend": [],
                "expense_breakdown": [],
                "total_revenue": 0,
                "total_expenses": 0,
                "net_profit": 0,
                "profit_margin": 0
            },
            "delivery": {
                "status_distribution": [],
                "delivery_map": [],
                "completion_rate": 0,
                "total_deliveries": 0
            },
            "inventory": {
                "low_stock_count": 0,
                "total_products": 0,
                "categories": [],
                "restock_alerts": []
            },
            "automation": {
                "notification_stats": [],
                "task_execution": {}
            }
        }, status=200)
    
    # Parse date range
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    if request.GET.get('start_date'):
        from datetime import datetime
        start_date = timezone.make_aware(datetime.strptime(request.GET['start_date'], '%Y-%m-%d'))
    if request.GET.get('end_date'):
        from datetime import datetime
        end_date = timezone.make_aware(datetime.strptime(request.GET['end_date'], '%Y-%m-%d'))
    
    # === FINANCIAL METRICS ===
    financial_data = _get_financial_metrics(tenant, start_date, end_date, days)
    
    # === DELIVERY METRICS ===
    delivery_data = _get_delivery_metrics(tenant, start_date, end_date)
    
    # === INVENTORY METRICS ===
    inventory_data = _get_inventory_metrics(tenant)
    
    # === AUTOMATION METRICS ===
    automation_data = _get_automation_metrics(tenant, start_date, end_date)
    
    return Response({
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": days
        },
        "financial": financial_data,
        "delivery": delivery_data,
        "inventory": inventory_data,
        "automation": automation_data,
        "summary": {
            "total_orders": Order.objects.filter(tenant=tenant, created_at__range=[start_date, end_date]).count(),
            "active_deliveries": Delivery.objects.filter(tenant=tenant, status__in=['assigned', 'picked_up', 'in_transit']).count(),
            "pending_notifications": Notification.objects.filter(recipient__tenant=tenant, read=False).count(),
        }
    })


def _get_financial_metrics(tenant, start_date, end_date, days):
    """Calculate financial metrics for 3D visualization"""
    
    # Revenue trend - daily aggregation
    orders = Order.objects.filter(
        tenant=tenant,
        created_at__range=[start_date, end_date],
        status__in=['paid', 'placed']  # Order statuses in POS app
    ).order_by('created_at')
    
    revenue_by_day = {}
    for order in orders:
        day_key = order.created_at.date().isoformat()
        if day_key not in revenue_by_day:
            revenue_by_day[day_key] = {"revenue": Decimal('0'), "orders": 0}
        revenue_by_day[day_key]["revenue"] += order.total
        revenue_by_day[day_key]["orders"] += 1
    
    revenue_trend = [
        {"date": date, "revenue": float(data["revenue"]), "orders": data["orders"]}
        for date, data in sorted(revenue_by_day.items())
    ]
    
    # Expense breakdown by category
    expenses = Expense.objects.filter(
        tenant=tenant,
        expense_date__range=[start_date.date(), end_date.date()]
    ).values('category').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('-total')
    
    expense_breakdown = [
        {
            "category": exp['category'],
            "amount": float(exp['total']),
            "count": exp['count']
        }
        for exp in expenses
    ]
    
    # Profit margin trend (weekly aggregation)
    total_revenue = sum(d['revenue'] for d in revenue_trend)
    total_expenses = sum(e['amount'] for e in expense_breakdown)
    profit_margin = ((total_revenue - total_expenses) / total_revenue * 100) if total_revenue > 0 else 0
    
    # Payment method distribution
    payments = Payment.objects.filter(
        tenant=tenant,
        created_at__range=[start_date, end_date],
        status='completed'
    ).values('provider').annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    payment_methods = [
        {
            "method": p['provider'],
            "amount": float(p['total']),
            "count": p['count']
        }
        for p in payments
    ]
    
    return {
        "revenue_trend": revenue_trend,
        "expense_breakdown": expense_breakdown,
        "payment_methods": payment_methods,
        "total_revenue": float(total_revenue),
        "total_expenses": float(total_expenses),
        "net_profit": float(total_revenue - total_expenses),
        "profit_margin": float(profit_margin)
    }


def _get_delivery_metrics(tenant, start_date, end_date):
    """Calculate delivery metrics for 3D map visualization"""
    
    # Status distribution
    deliveries = Delivery.objects.filter(
        tenant=tenant,
        created_at__range=[start_date, end_date]
    )
    
    status_dist = deliveries.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    status_distribution = [
        {
            "status": s['status'],
            "count": s['count'],
            "percentage": (s['count'] / deliveries.count() * 100) if deliveries.count() > 0 else 0
        }
        for s in status_dist
    ]
    
    # Delivery map data (with GPS coordinates)
    delivery_map = []
    for delivery in deliveries.select_related('address', 'delivery_person')[:100]:  # Limit for performance
        if delivery.address and delivery.address.latitude and delivery.address.longitude:
            delivery_map.append({
                "id": delivery.id,
                "lat": float(delivery.address.latitude),
                "lon": float(delivery.address.longitude),
                "status": delivery.status,
                "city": delivery.address.city or "Unknown",
                "personnel": delivery.delivery_person.name if delivery.delivery_person else None
            })
    
    # Completion metrics
    total_deliveries = deliveries.count()
    completed = deliveries.filter(status='delivered').count()
    failed = deliveries.filter(status='failed').count()
    completion_rate = (completed / total_deliveries * 100) if total_deliveries > 0 else 0
    
    return {
        "status_distribution": status_distribution,
        "delivery_map": delivery_map,
        "total_deliveries": total_deliveries,
        "completed": completed,
        "failed": failed,
        "in_progress": total_deliveries - completed - failed,
        "completion_rate": float(completion_rate),
        "avg_delivery_time_hours": None  # Would need additional timestamp fields
    }


def _get_inventory_metrics(tenant):
    """Calculate inventory metrics for 3D visualization"""
    
    products = Product.objects.filter(tenant=tenant)
    
    # Low stock products
    low_stock = products.filter(
        quantity__lte=F('low_stock_threshold')
    ).exclude(low_stock_threshold=0)
    
    low_stock_count = low_stock.count()
    
    # Category distribution
    category_stats = products.values('category').annotate(
        total_quantity=Sum('quantity'),
        product_count=Count('id'),
        low_stock_items=Count('id', filter=Q(quantity__lte=F('low_stock_threshold')))
    ).order_by('-total_quantity')
    
    categories = [
        {
            "category": cat['category'] or 'Uncategorized',
            "quantity": cat['total_quantity'] or 0,
            "products": cat['product_count'],
            "low_stock": cat['low_stock_items']
        }
        for cat in category_stats
    ]
    
    # Restock alerts (critical items)
    restock_alerts = []
    for product in low_stock[:20]:  # Top 20 critical items
        restock_alerts.append({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "current_quantity": product.quantity,
            "threshold": product.low_stock_threshold,
            "shortage": max(0, product.low_stock_threshold - product.quantity),
            "category": product.category or "Uncategorized"
        })
    
    # Inventory value
    total_value = sum(
        (p.quantity * (p.cost_price or Decimal('0')))
        for p in products
    )
    
    return {
        "low_stock_count": low_stock_count,
        "total_products": products.count(),
        "categories": categories,
        "restock_alerts": restock_alerts,
        "total_inventory_value": float(total_value)
    }


def _get_automation_metrics(tenant, start_date, end_date):
    """Calculate automation and task execution metrics"""
    
    # Notification statistics
    notifications = Notification.objects.filter(
        recipient__tenant=tenant,
        created_at__range=[start_date, end_date]
    )
    
    # Group by channel since notification_type doesn't exist
    notif_by_channel = notifications.values('channel').annotate(
        count=Count('id'),
        read_count=Count('id', filter=Q(read=True))
    ).order_by('-count')
    
    notification_stats = [
        {
            "type": n['channel'] or 'general',
            "total": n['count'],
            "read": n['read_count'],
            "unread": n['count'] - n['read_count']
        }
        for n in notif_by_channel
    ]
    
    # Task execution simulation (estimate based on notification counts)
    task_types = {
        "notifications_sent": notifications.count(),
        "emails": notifications.filter(channel='email').count(),
        "in_app": notifications.filter(channel='in_app').count(),
    }
    
    # Recent activity timeline
    recent_notifications = notifications.order_by('-created_at')[:50]
    activity_timeline = [
        {
            "time": n.created_at.isoformat(),
            "type": n.channel or 'general',
            "title": n.title,
            "read": n.read
        }
        for n in recent_notifications
    ]
    
    return {
        "notification_stats": notification_stats,
        "task_execution": task_types,
        "activity_timeline": activity_timeline,
        "total_notifications": notifications.count(),
        "unread_notifications": notifications.filter(read=False).count()
    }
