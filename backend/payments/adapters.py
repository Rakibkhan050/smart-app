from abc import ABC, abstractmethod
import uuid
from django.conf import settings


class PaymentAdapter(ABC):
    """Abstract payment adapter interface for creating payment intents and verifying webhooks."""

    @abstractmethod
    def create_payment_intent(self, amount, currency='SAR', metadata=None):
        pass

    @abstractmethod
    def verify_webhook(self, payload, headers):
        pass


class SandboxAdapter(PaymentAdapter):
    """Simple sandbox adapter that fakes intents and webhooks for local testing."""

    def create_payment_intent(self, amount, currency='SAR', metadata=None):
        # Return a fake client secret and an id
        return {
            'id': f'sandbox_{uuid.uuid4().hex[:8]}',
            'client_secret': f'sandbox_secret_{uuid.uuid4().hex}',
            'amount': float(amount),
            'currency': currency,
        }

    def verify_webhook(self, payload, headers):
        # For sandbox, accept a header 'X-SANDBOX-SIGN' == 'ok' as valid
        if headers.get('X-SANDBOX-SIGN') == 'ok':
            # return parsed payload (simply return request data for testing)
            try:
                return payload if isinstance(payload, dict) else {}
            except Exception:
                return {}
        return False


# Specific provider stubs - they can be implemented later to call real SDKs
class StripeAdapter(SandboxAdapter):
    """Stripe adapter using stripe-python SDK. 
    
    Supports:
    - Real Stripe (STRIPE_API_KEY + STRIPE_WEBHOOK_SECRET env vars)
    - stripe-mock via Docker (USE_STRIPE_MOCK=True env var)
    - Sandbox mode (fallback)
    """

    def __init__(self):
        try:
            import stripe
            self.stripe = stripe
        except Exception:
            self.stripe = None

    def _get_stripe_client(self):
        """Get Stripe client configured for either real or mock API."""
        if not self.stripe:
            raise RuntimeError('stripe package not installed')
        
        use_mock = getattr(settings, 'USE_STRIPE_MOCK', False)
        if use_mock:
            # Point to stripe-mock Docker service
            self.stripe.api_base = getattr(settings, 'STRIPE_MOCK_URL', 'http://stripe-mock:12111')
            self.stripe.api_key = 'sk_test_mock'
        else:
            # Real Stripe API
            if not getattr(settings, 'STRIPE_API_KEY', None):
                raise RuntimeError('STRIPE_API_KEY not configured')
            self.stripe.api_key = settings.STRIPE_API_KEY
        
        return self.stripe

    def create_payment_intent(self, amount, currency='SAR', metadata=None):
        try:
            stripe_client = self._get_stripe_client()
            intent = stripe_client.PaymentIntent.create(
                amount=int(float(amount) * 100),
                currency=(currency or 'sar').lower(),
                metadata=metadata or {}
            )
            return {
                'id': intent.id,
                'client_secret': getattr(intent, 'client_secret', None),
                'amount': float(amount),
                'currency': currency
            }
        except Exception as e:
            # Fallback to sandbox on error
            return super().create_payment_intent(amount, currency, metadata)

    def verify_webhook(self, payload, headers):
        if not self.stripe:
            return False
        
        use_mock = getattr(settings, 'USE_STRIPE_MOCK', False)
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        sig = headers.get('Stripe-Signature') or headers.get('stripe-signature')
        
        if not endpoint_secret or not sig:
            return False
        
        try:
            if use_mock:
                # stripe-mock uses same webhook signature verification
                self.stripe.api_base = getattr(settings, 'STRIPE_MOCK_URL', 'http://stripe-mock:12111')
                self.stripe.api_key = 'sk_test_mock'
            else:
                self.stripe.api_key = settings.STRIPE_API_KEY
            
            event = self.stripe.Webhook.construct_event(payload, sig, endpoint_secret)
            return event
        except Exception:
            return False


class HyperPayAdapter(SandboxAdapter):
    pass


class ApplePayAdapter(SandboxAdapter):
    pass


class GooglePayAdapter(SandboxAdapter):
    pass


class WalletsAdapter(SandboxAdapter):
    pass


# Helper factory
def get_adapter(provider='sandbox'):
    provider = (provider or '').lower()
    if provider in ('stripe', 'visa_mastercard'):
        return StripeAdapter()
    if provider in ('hyperpay', 'tap', 'paytabs'):
        return HyperPayAdapter()
    if provider == 'apple_pay':
        return ApplePayAdapter()
    if provider == 'google_pay':
        return GooglePayAdapter()
    if provider == 'wallet':
        return WalletsAdapter()
    return SandboxAdapter()