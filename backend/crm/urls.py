from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    CustomerViewSet, LoyaltyPointViewSet, SupplierViewSet,
    LoyaltyTransactionViewSet, PurchaseHistoryViewSet
)

router = DefaultRouter()
router.register('customers', CustomerViewSet, basename='customer')
router.register('loyalty', LoyaltyPointViewSet, basename='loyalty')
router.register('loyalty-transactions', LoyaltyTransactionViewSet, basename='loyalty-transaction')
router.register('purchase-history', PurchaseHistoryViewSet, basename='purchase-history')
router.register('suppliers', SupplierViewSet, basename='supplier')

urlpatterns = [
    path('', include(router.urls)),
]
