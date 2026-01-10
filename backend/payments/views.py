from rest_framework import views, response, permissions


class CreatePaymentIntentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Placeholder: create payment intent with provider (PayTabs/Tap/HyperPay)
        # In real implementation, call provider API and return session data
        return response.Response({'status': 'created', 'payment_id': 'pi_123'})


class PaymentWebhookView(views.APIView):
    permission_classes = []

    def post(self, request):
        # Handle webhook payload from payment provider
        # Example signature verification placeholder
        sig = request.headers.get('X-PAYMENT-SIGNATURE')
        secret = getattr(request._request, 'PAYMENT_SECRET', None) or None
        # TODO: verify signature using provider docs
        # For now, accept and respond OK
        return response.Response({'status': 'ok'})
