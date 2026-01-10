from django.urls import path
from .views import CreatePaymentIntentView, PaymentWebhookView

urlpatterns = [
    path('create-intent/', CreatePaymentIntentView.as_view(), name='create_intent'),
    path('webhook/', PaymentWebhookView.as_view(), name='payment_webhook'),
]
