from django.urls import path
from . import location_api

urlpatterns = [
    # Real-time Location Tracking
    path('location/update/', location_api.update_driver_location, name='update-driver-location'),
    path('track/<str:tracking_number>/', location_api.track_delivery, name='track-delivery'),
    path('<uuid:driver_id>/location-history/', location_api.driver_location_history, name='driver-location-history'),
    path('nearby/', location_api.nearby_drivers, name='nearby-drivers'),
]
