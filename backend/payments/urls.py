from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreatePaymentIntentView, PaymentWebhookView, TestWebhookView
from .api import PaymentViewSet, ReceiptViewSet

router = DefaultRouter()
router.register('payments', PaymentViewSet, basename='payment')
router.register('receipts', ReceiptViewSet, basename='receipt')

urlpatterns = [
    path('', include(router.urls)),
    path('create-intent/', CreatePaymentIntentView.as_view(), name='create_intent'),
    path('webhook/', PaymentWebhookView.as_view(), name='payment_webhook'),
    path('test-webhook/', TestWebhookView.as_view(), name='test_webhook'),
]
