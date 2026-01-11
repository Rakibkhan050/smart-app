from django.urls import path
from . import storefront_api, master_admin_api

urlpatterns = [
    # Storefront API (Customer-facing)
    path('storefront/businesses/', storefront_api.storefront_businesses, name='storefront-businesses'),
    path('storefront/businesses/<slug:business_slug>/', storefront_api.storefront_business_detail, name='storefront-business-detail'),
    path('storefront/categories/', storefront_api.storefront_categories, name='storefront-categories'),
    
    # Master Admin API
    path('master-admin/dashboard/', master_admin_api.master_dashboard, name='master-admin-dashboard'),
    path('master-admin/businesses/<int:business_id>/commission/', master_admin_api.update_commission_rate, name='update-commission'),
]
