from rest_framework import views, response, permissions


class CreatePaymentIntentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Placeholder: create payment intent with provider (PayTabs/Tap/HyperPay)
        return response.Response({'status': 'created', 'payment_id': 'pi_123'})


class PaymentWebhookView(views.APIView):
    permission_classes = []

    def post(self, request):
        # Handle webhook payload from payment provider
        return response.Response({'status': 'ok'})
