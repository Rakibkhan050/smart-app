"""
Master Admin Dashboard API
Platform-wide analytics, commission tracking, and management
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from tenants.models import Tenant
from pos.models import Order
from payments.models import Payment
from drivers.models import Driver, DriverAssignment
from crm.models import Customer
from users.models import User
from drivers.models import DriverProfile


@api_view(['GET'])
@permission_classes([IsAdminUser])
def master_dashboard(request):
    """
    Master Admin Dashboard - Platform-wide overview
    """
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Total businesses
    total_businesses = Tenant.objects.count()
    active_businesses = Tenant.objects.filter(is_active=True, is_approved=True).count()
    pending_approval = Tenant.objects.filter(is_approved=False).count()
    
    # Revenue metrics
    total_platform_sales = Tenant.objects.aggregate(
        total=Sum('total_sales')
    )['total'] or Decimal('0')
    
    total_platform_commission = Tenant.objects.aggregate(
        total=Sum('total_commission')
    )['total'] or Decimal('0')
    
    # Recent orders across all businesses
    recent_orders = Order.objects.filter(
        created_at__range=[start_date, end_date]
    ).count()
    
    total_order_value = Order.objects.filter(
        created_at__range=[start_date, end_date]
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    # Payment method distribution
    payment_distribution = Payment.objects.filter(
        created_at__range=[start_date, end_date],
        status='completed'
    ).values('provider').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')
    
    # Driver statistics
    total_drivers = Driver.objects.count()
    active_drivers = Driver.objects.filter(status='available').count()
    total_deliveries = DriverAssignment.objects.filter(
        assigned_at__range=[start_date, end_date]
    ).count()
    completed_deliveries = DriverAssignment.objects.filter(
        assigned_at__range=[start_date, end_date],
        is_completed=True
    ).count()
    
    # Customer statistics
    total_customers = Customer.objects.count()
    new_customers = Customer.objects.filter(
        created_at__range=[start_date, end_date]
    ).count()
    
    # Top performing businesses
    top_businesses = Tenant.objects.filter(
        is_active=True,
        is_approved=True
    ).order_by('-total_sales')[:10]
    
    top_businesses_data = []
    for business in top_businesses:
        top_businesses_data.append({
            'id': business.id,
            'name': business.name,
            'category': business.get_category_display(),
            'total_sales': float(business.total_sales),
            'total_commission': float(business.total_commission),
            'commission_rate': float(business.commission_rate),
        })
    
    # Category breakdown
    category_stats = []
    for choice in Tenant.CATEGORY_CHOICES:
        businesses_count = Tenant.objects.filter(
            category=choice[0],
            is_active=True,
            is_approved=True
        ).count()
        
        category_sales = Tenant.objects.filter(
            category=choice[0],
            is_active=True,
            is_approved=True
        ).aggregate(total=Sum('total_sales'))['total'] or Decimal('0')
        
        category_stats.append({
            'category': choice[1],
            'businesses_count': businesses_count,
            'total_sales': float(category_sales)
        })
    
    return Response({
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'days': days
        },
        'businesses': {
            'total': total_businesses,
            'active': active_businesses,
            'pending_approval': pending_approval,
            'by_category': category_stats
        },
        'revenue': {
            'total_platform_sales': float(total_platform_sales),
            'total_platform_commission': float(total_platform_commission),
            'net_to_businesses': float(total_platform_sales - total_platform_commission),
            'recent_orders_count': recent_orders,
            'recent_orders_value': float(total_order_value),
            'payment_distribution': [
                {
                    'method': p['provider'],
                    'count': p['count'],
                    'total': float(p['total'])
                }
                for p in payment_distribution
            ]
        },
        'drivers': {
            'total': total_drivers,
            'active': active_drivers,
            'total_deliveries': total_deliveries,
            'completed_deliveries': completed_deliveries,
            'completion_rate': (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        },
        'customers': {
            'total': total_customers,
            'new_this_period': new_customers
        },
        'top_businesses': top_businesses_data
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_commission_rate(request, business_id):
    """
    Update commission rate for a specific business
    """
    try:
        business = Tenant.objects.get(id=business_id)
    except Tenant.DoesNotExist:
        return Response({'error': 'Business not found'}, status=404)
    
    new_rate = request.data.get('commission_rate')
    
    if new_rate is None:
        return Response({'error': 'commission_rate is required'}, status=400)
    
    try:
        new_rate = Decimal(str(new_rate))
        if new_rate < 0 or new_rate > 100:
            return Response({'error': 'Commission rate must be between 0 and 100'}, status=400)
    except:
        return Response({'error': 'Invalid commission rate'}, status=400)
    
    business.commission_rate = new_rate
    business.save()
    
    return Response({
        'success': True,
        'business': business.name,
        'new_commission_rate': float(new_rate)
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def global_search(request):
    """
    Master Admin - Global search across Customers and Drivers by
    registration_id or mobile/email.
    Query params:
      - q: the search text
      - type: 'customer' | 'driver' | 'business' (optional)
    """
    q = (request.GET.get('q') or '').strip()
    t = (request.GET.get('type') or '').strip()
    if not q:
        return Response({'error': 'q is required'}, status=400)
    
    results = {
        'customers': [],
        'drivers': [],
        'businesses': []
    }
    
    # Customers across all tenants
    if not t or t == 'customer':
        for cust in Customer.objects.filter(
            Q(phone__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )[:50]:
            results['customers'].append({
                'id': cust.id,
                'name': f"{cust.first_name} {cust.last_name}".strip(),
                'phone': cust.phone,
                'email': cust.email,
                'tenant': cust.tenant.name if cust.tenant else None,
            })
    
    # Drivers across all tenants
    if not t or t == 'driver':
        for drv in DriverProfile.objects.filter(
            Q(mobile_number__icontains=q) | Q(registration_id__icontains=q) | Q(full_name__icontains=q)
        )[:50]:
            results['drivers'].append({
                'id': drv.id,
                'name': drv.full_name,
                'mobile_number': drv.mobile_number,
                'registration_id': drv.registration_id,
                'status': drv.verification_status,
            })
    
    # Businesses by registration_id or name
    if not t or t == 'business':
        for biz in Tenant.objects.filter(
            Q(registration_id__icontains=q) | Q(name__icontains=q)
        )[:50]:
            results['businesses'].append({
                'id': str(biz.id),
                'name': biz.name,
                'registration_id': biz.registration_id,
                'category': biz.get_category_display(),
                'owner_email': biz.owner_email,
            })
    
    return Response({'query': q, 'results': results})
