"""
Storefront API - Customer-facing views to browse businesses and products
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Q
from tenants.models import Tenant
from inventory.models import Product
from pos.models import Order


@api_view(['GET'])
@permission_classes([AllowAny])
def storefront_businesses(request):
    """
    List all active and approved businesses for customers
    Filter by category, search by name
    """
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    businesses = Tenant.objects.filter(
        is_active=True,
        is_approved=True
    )
    
    if category:
        businesses = businesses.filter(category=category)
    
    if search:
        businesses = businesses.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Annotate with stats
    businesses = businesses.annotate(
        product_count=Count('product', distinct=True),
        order_count=Count('order', distinct=True)
    )
    
    data = []
    for business in businesses:
        data.append({
            'id': business.id,
            'name': business.name,
            'slug': business.slug,
            'category': business.category,
            'category_display': business.get_category_display(),
            'description': business.description,
            'logo': business.logo,
            'product_count': business.product_count,
            'order_count': business.order_count,
            'owner_name': business.owner_name,
            'business_address': business.business_address,
        })
    
    return Response({
        'total': len(data),
        'businesses': data,
        'categories': [
            {'value': choice[0], 'label': choice[1]}
            for choice in Tenant.CATEGORY_CHOICES
        ]
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def storefront_business_detail(request, business_slug):
    """
    Get details of a specific business and its products
    """
    try:
        business = Tenant.objects.get(
            slug=business_slug,
            is_active=True,
            is_approved=True
        )
    except Tenant.DoesNotExist:
        return Response({'error': 'Business not found'}, status=404)
    
    # Get products for this business
    products = Product.objects.filter(tenant=business)
    
    # Apply filters
    category = request.GET.get('product_category')
    search = request.GET.get('search')
    
    if category:
        products = products.filter(category=category)
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(brand__icontains=search)
        )
    
    products = products[:50]  # Limit to 50 products
    
    product_data = []
    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'category': product.category,
            'sku': product.sku,
            'barcode': product.barcode,
            'unit': product.unit,
            'quantity': product.quantity,
            'sell_price': float(product.sell_price),
            'is_available': product.quantity > 0,
            'is_low_stock': product.is_low_stock(),
        })
    
    return Response({
        'business': {
            'id': business.id,
            'name': business.name,
            'slug': business.slug,
            'category': business.category,
            'category_display': business.get_category_display(),
            'description': business.description,
            'logo': business.logo,
            'owner_name': business.owner_name,
            'business_address': business.business_address,
        },
        'products': product_data,
        'total_products': len(product_data)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def storefront_categories(request):
    """
    Get business categories with counts
    """
    categories = []
    for choice in Tenant.CATEGORY_CHOICES:
        count = Tenant.objects.filter(
            category=choice[0],
            is_active=True,
            is_approved=True
        ).count()
        
        categories.append({
            'value': choice[0],
            'label': choice[1],
            'count': count
        })
    
    return Response({
        'categories': categories,
        'total_businesses': Tenant.objects.filter(
            is_active=True,
            is_approved=True
        ).count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def storefront_manifest(request, business_slug):
    """
    Return manifest.json for a specific business storefront based on StorefrontConfig.
    """
    try:
        business = Tenant.objects.get(
            slug=business_slug,
            is_active=True,
            is_approved=True
        )
    except Tenant.DoesNotExist:
        return Response({'error': 'Business not found'}, status=404)
    sf = getattr(business, 'storefront', None)
    if not sf:
        return Response({'error': 'Storefront not configured'}, status=404)
    return Response(sf.manifest())
