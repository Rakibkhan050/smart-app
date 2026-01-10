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
        provider = request.headers.get('X-PAYMENT-PROVIDER', 'paytabs').lower()
        signature = request.headers.get('X-PAYMENT-SIGNATURE', '')
        from .utils import get_provider_secret, verify_paytabs_signature, verify_tap_signature, verify_hyperpay_signature
        secret = get_provider_secret(provider)
        body = request.body or b''

        verified = False
        if provider == 'paytabs':
            verified = verify_paytabs_signature(body, signature, secret)
        elif provider == 'tap':
            verified = verify_tap_signature(body, signature, secret)
        elif provider == 'hyperpay':
            verified = verify_hyperpay_signature(body, signature, secret)

        if not verified:
            return response.Response({'status': 'forbidden', 'detail': 'invalid signature'}, status=403)

        # parse minimal payload - production: validate more carefully
        data = request.data
        payment_id = data.get('payment_id') or data.get('transaction_id') or data.get('id')
        amount = data.get('amount')
        currency = data.get('currency')

        # Enqueue receipt generation task
        from receipts.tasks import generate_receipt_for_payment
        generate_receipt_for_payment.delay(payment_id=payment_id, amount=amount, currency=currency)

        return response.Response({'status': 'ok'})
