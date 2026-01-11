from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    DeliveryViewSet, DeliveryPersonnelViewSet, 
    AddressViewSet, ShippingFeeRuleViewSet
)

router = DefaultRouter()
router.register('deliveries', DeliveryViewSet, basename='delivery')
router.register('personnel', DeliveryPersonnelViewSet, basename='personnel')
router.register('addresses', AddressViewSet, basename='address')
router.register('shipping-fees', ShippingFeeRuleViewSet, basename='shipping-fee')

urlpatterns = [    path('', include(router.urls)),
]