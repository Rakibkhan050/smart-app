from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import TaxRateViewSet, ExpenseViewSet, ReportViewSet
from .dashboard_api import dashboard_3d_metrics

router = DefaultRouter()
router.register('tax-rates', TaxRateViewSet, basename='tax-rate')
router.register('expenses', ExpenseViewSet, basename='expense')
router.register('reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/3d-metrics/', dashboard_3d_metrics, name='dashboard-3d-metrics'),
]
