from django.contrib import admin
from django.urls import path, include

# Customize Admin Site Header
admin.site.site_header = "Multi-Business SaaS Platform - Master Admin"
admin.site.site_title = "Master Admin Portal"
admin.site.index_title = "Platform Management Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/auth/', include('users.urls')),
    
    # Core APIs
    path('api/', include('notifications.urls')),
    path('api/receipts/', include('receipts.urls')),
    path('api/payments/', include('payments.urls')),
    
    # Business Operations
    path('api/inventory/', include('inventory.urls')),
    path('api/pos/', include('pos.urls')),
    
    # Customer & Delivery
    path('api/crm/', include('crm.urls')),
    path('api/delivery/', include('delivery.urls')),
    path('api/drivers/', include('drivers.urls')),  # Driver location tracking
    
    # Analytics & Finance
    path('api/finance/', include('finance.urls')),
    
    # Multi-Business SaaS APIs
    path('api/', include('tenants.urls')),  # Storefront & Master Admin APIs
]
