from rest_framework import views, response, permissions
from .adapters import get_adapter


class CreatePaymentIntentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        amount = data.get('amount')
        currency = data.get('currency', 'SAR')
        provider = data.get('provider', 'sandbox')
        if amount is None:
            return response.Response({'detail': 'amount is required'}, status=400)

        adapter = get_adapter(provider)
        intent = adapter.create_payment_intent(amount=amount, currency=currency, metadata=data.get('metadata'))
        return response.Response(intent, status=201)


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


class TestWebhookView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # convenience endpoint for local dev to simulate a webhook and bypass signature checks
        data = request.data
        payment_id = data.get('payment_id', 'test_1')
        amount = data.get('amount', 0)
        from receipts.tasks import generate_receipt_for_payment
        try:
            generate_receipt_for_payment.delay(payment_id=payment_id, amount=amount, currency=data.get('currency', 'SAR'))
        except Exception:
            # If Celery broker is unavailable (dev/test), try to call the underlying function synchronously
            try:
                func = getattr(generate_receipt_for_payment, '__wrapped__', None)
                if func:
                    func(None, payment_id=payment_id, amount=amount, currency=data.get('currency', 'SAR'))
            except Exception:
                pass
        return response.Response({'status': 'ok', 'payment_id': payment_id})


class PaymentWebhookView(views.APIView):
    permission_classes = []

    def post(self, request):
        # Unified webhook handler (supports paytabs/tap/hyperpay and stripe)
        provider = request.headers.get('X-PAYMENT-PROVIDER', 'paytabs').lower()
        body = request.body or b''

        # special case: stripe uses its own signature header and verification
        if provider in ('stripe', 'stripe_api'):
            adapter = get_adapter('stripe')
            event = adapter.verify_webhook(body, request.headers)
            if not event:
                return response.Response({'status': 'forbidden', 'detail': 'invalid signature'}, status=403)
            # Example: handle payment_intent.succeeded
            ev_type = getattr(event, 'get', None) and event.get('type') or None
            data_obj = None
            if ev_type and 'data' in event:
                data_obj = event['data'].get('object')
            if data_obj is None:
                # fallback to basic body parsing
                data = request.data
                payment_id = data.get('payment_id') or data.get('id')
                amount = data.get('amount')
                currency = data.get('currency')
            else:
                payment_id = data_obj.get('id') or (data_obj.get('metadata') or {}).get('payment_id')
                amount = (data_obj.get('amount') or 0) / 100.0 if data_obj.get('amount') else None
                currency = data_obj.get('currency')

            from receipts.tasks import generate_receipt_for_payment
            if payment_id:
                generate_receipt_for_payment.delay(payment_id=payment_id, amount=amount, currency=currency)
            return response.Response({'status': 'ok'})

        # legacy providers
        signature = request.headers.get('X-PAYMENT-SIGNATURE', '')
        from .utils import get_provider_secret, verify_paytabs_signature, verify_tap_signature, verify_hyperpay_signature
        secret = get_provider_secret(provider)

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
