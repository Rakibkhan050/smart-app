"""
Real-time Location Tracking API for Drivers
Provides live location updates and tracking for deliveries
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from decimal import Decimal

from .models import DriverProfile, DriverAssignment, LocationHistory
from delivery.models import Delivery
from tenants.models import Tenant


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_driver_location(request):
    """
    Driver updates their current location (called from mobile app)
    
    Body:
    {
        "latitude": 24.7136,
        "longitude": 46.6753,
        "accuracy": 10,
        "speed": 25.5,
        "heading": 180
    }
    """
    try:
        driver = request.user.driver_profile
    except DriverProfile.DoesNotExist:
        return Response({'error': 'Driver profile not found'}, status=404)
    
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if not latitude or not longitude:
        return Response({'error': 'latitude and longitude required'}, status=400)
    
    try:
        lat = Decimal(str(latitude))
        lon = Decimal(str(longitude))
    except:
        return Response({'error': 'Invalid coordinates'}, status=400)
    
    # Update driver location
    driver.current_latitude = lat
    driver.current_longitude = lon
    driver.last_location_update = timezone.now()
    driver.save(update_fields=['current_latitude', 'current_longitude', 'last_location_update'])
    
    # Get active assignment for location trail
    active_assignment = DriverAssignment.objects.filter(
        driver=driver,
        status='in_progress'
    ).first()
    
    if active_assignment:
        # Create location history point
        LocationHistory.objects.create(
            driver=driver,
            assignment=active_assignment,
            latitude=lat,
            longitude=lon,
            accuracy=request.data.get('accuracy'),
            speed=request.data.get('speed'),
            heading=request.data.get('heading')
        )
    
    return Response({
        'success': True,
        'location': {
            'latitude': float(lat),
            'longitude': float(lon),
            'timestamp': driver.last_location_update.isoformat()
        },
        'active_assignment': active_assignment.id if active_assignment else None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def track_delivery(request, tracking_number):
    """
    Public endpoint to track delivery by tracking number
    Returns current driver location and delivery status
    
    GET /api/drivers/track/<tracking_number>/
    """
    try:
        delivery = Delivery.objects.get(tracking_number=tracking_number)
    except Delivery.DoesNotExist:
        return Response({'error': 'Delivery not found'}, status=404)
    
    # Get driver assignment if exists
    assignment = DriverAssignment.objects.filter(
        delivery=delivery,
        status__in=['assigned', 'in_progress']
    ).first()
    
    response_data = {
        'tracking_number': delivery.tracking_number,
        'order_reference': delivery.order_reference,
        'status': delivery.status,
        'status_display': delivery.get_status_display(),
        'expected_delivery': delivery.expected_delivery.isoformat() if delivery.expected_delivery else None,
        'created_at': delivery.created_at.isoformat(),
        'updated_at': delivery.updated_at.isoformat(),
    }
    
    # Add pickup and destination coordinates
    if delivery.address:
        response_data['destination'] = {
            'latitude': float(delivery.address.latitude) if delivery.address.latitude else None,
            'longitude': float(delivery.address.longitude) if delivery.address.longitude else None,
            'address': delivery.address.line1,
            'city': delivery.address.city
        }
    
    # Add driver location if in transit
    if assignment and assignment.driver:
        driver = assignment.driver
        if driver.current_latitude and driver.current_longitude:
            # Only show location if recently updated (within 5 minutes)
            if driver.last_location_update and \
               (timezone.now() - driver.last_location_update) < timedelta(minutes=5):
                response_data['driver'] = {
                    'name': driver.full_name,
                    'phone': driver.mobile_number,
                    'vehicle_type': driver.vehicle_type,
                    'vehicle_number': driver.vehicle_number,
                    'current_location': {
                        'latitude': float(driver.current_latitude),
                        'longitude': float(driver.current_longitude),
                        'last_updated': driver.last_location_update.isoformat()
                    },
                    'status': driver.status
                }
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_location_history(request, driver_id):
    """
    Get location trail/history for a specific driver and assignment
    Used to show path traveled
    
    GET /api/drivers/<driver_id>/location-history/?assignment_id=<id>&hours=<hours>
    """
    try:
        driver = DriverProfile.objects.get(id=driver_id)
    except DriverProfile.DoesNotExist:
        return Response({'error': 'Driver not found'}, status=404)
    
    # Business owners can see their drivers
    user = request.user
    if not user.is_superuser:
        if hasattr(user, 'tenant'):
            if user.tenant not in driver.assigned_businesses.all():
                return Response({'error': 'Unauthorized'}, status=403)
        else:
            return Response({'error': 'Unauthorized'}, status=403)
    
    assignment_id = request.GET.get('assignment_id')
    hours = int(request.GET.get('hours', 2))
    
    since = timezone.now() - timedelta(hours=hours)
    
    history_qs = LocationHistory.objects.filter(
        driver=driver,
        timestamp__gte=since
    ).order_by('timestamp')
    
    if assignment_id:
        history_qs = history_qs.filter(assignment_id=assignment_id)
    
    locations = []
    for loc in history_qs:
        locations.append({
            'latitude': float(loc.latitude),
            'longitude': float(loc.longitude),
            'timestamp': loc.timestamp.isoformat(),
            'speed': float(loc.speed) if loc.speed else None,
            'heading': float(loc.heading) if loc.heading else None,
            'accuracy': float(loc.accuracy) if loc.accuracy else None,
        })
    
    return Response({
        'driver_id': str(driver.id),
        'driver_name': driver.full_name,
        'locations': locations,
        'total_points': len(locations),
        'time_range': {
            'start': since.isoformat(),
            'end': timezone.now().isoformat()
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nearby_drivers(request):
    """
    Find available drivers nearby a location
    Used for dispatch/assignment
    
    GET /api/drivers/nearby/?latitude=<lat>&longitude=<lon>&radius=<km>&tenant_id=<id>
    """
    lat = request.GET.get('latitude')
    lon = request.GET.get('longitude')
    radius_km = float(request.GET.get('radius', 10))
    tenant_id = request.GET.get('tenant_id')
    
    if not lat or not lon:
        return Response({'error': 'latitude and longitude required'}, status=400)
    
    try:
        lat = Decimal(str(lat))
        lon = Decimal(str(lon))
    except:
        return Response({'error': 'Invalid coordinates'}, status=400)
    
    # Get available drivers
    drivers_qs = DriverProfile.objects.filter(
        is_active=True,
        verification_status='approved',
        status__in=['available', 'on_break'],
        current_latitude__isnull=False,
        current_longitude__isnull=False
    )
    
    # Filter by tenant if specified
    if tenant_id:
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            drivers_qs = drivers_qs.filter(assigned_businesses=tenant)
        except Tenant.DoesNotExist:
            pass
    
    # Calculate distance (simple approximation)
    # For production, use PostGIS or geopy for accurate distance
    nearby_drivers = []
    for driver in drivers_qs:
        if driver.current_latitude and driver.current_longitude:
            # Simple distance calculation (not accurate for long distances)
            lat_diff = abs(float(driver.current_latitude) - float(lat))
            lon_diff = abs(float(driver.current_longitude) - float(lon))
            approx_distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # rough km conversion
            
            if approx_distance <= radius_km:
                # Check if location is recent (within 10 minutes)
                if driver.last_location_update and \
                   (timezone.now() - driver.last_location_update) < timedelta(minutes=10):
                    nearby_drivers.append({
                        'id': str(driver.id),
                        'name': driver.full_name,
                        'phone': driver.mobile_number,
                        'vehicle_type': driver.vehicle_type,
                        'vehicle_number': driver.vehicle_number,
                        'status': driver.status,
                        'rating': float(driver.average_rating),
                        'current_location': {
                            'latitude': float(driver.current_latitude),
                            'longitude': float(driver.current_longitude),
                            'last_updated': driver.last_location_update.isoformat()
                        },
                        'distance_km': round(approx_distance, 2),
                        'total_deliveries': driver.total_deliveries,
                        'successful_deliveries': driver.successful_deliveries
                    })
    
    # Sort by distance
    nearby_drivers.sort(key=lambda x: x['distance_km'])
    
    return Response({
        'search_location': {
            'latitude': float(lat),
            'longitude': float(lon),
            'radius_km': radius_km
        },
        'drivers': nearby_drivers,
        'total_found': len(nearby_drivers)
    })
