from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/', include('notifications.urls')),
    path('api/receipts/', include('receipts.urls')),
    path('api/payments/', include('payments.urls')),
]
