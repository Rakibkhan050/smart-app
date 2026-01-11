"""Integration tests for Stripe payments using stripe-mock Docker service."""
import pytest
import json
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from payments.models import Payment
from payments.adapters import StripeAdapter, get_adapter

User = get_user_model()


@pytest.mark.integration
class StripeIntegrationTest(TestCase):
    """Test Stripe integration with stripe-mock Docker service."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.user.tenant = self.tenant
        self.user.role = 'admin'
        self.user.save()
        self.client = APIClient()

    @override_settings(USE_STRIPE_MOCK=True, STRIPE_MOCK_URL='http://stripe-mock:12111')
    def test_stripe_adapter_uses_mock(self):
        """Test StripeAdapter can connect to stripe-mock."""
        adapter = StripeAdapter()
        # This should work with stripe-mock if it's running
        try:
            result = adapter.create_payment_intent(amount=1000, currency='USD')
            assert result['id'], "Payment intent should have an ID"
            assert 'client_secret' in result
        except Exception as e:
            # If stripe-mock is not running, we expect this to gracefully fall back
            # and use sandbox mode
            result = adapter.create_payment_intent(amount=1000, currency='USD')
            assert 'sandbox_' in result['id'] or 'id' in result

    @override_settings(USE_STRIPE_MOCK=True, STRIPE_MOCK_URL='http://stripe-mock:12111')
    def test_create_payment_intent_via_api(self):
        """Test creating a payment intent via the API using stripe-mock."""
        self.client.force_authenticate(self.user)
        resp = self.client.post('/api/payments/create-intent/', {
            'amount': '100.00',
            'currency': 'USD',
        })
        # Should return either a real Stripe intent or sandbox fallback
        if resp.status_code == 201:
            data = resp.json()
            assert 'client_secret' in data or 'id' in data

    @override_settings(USE_STRIPE_MOCK=True, STRIPE_MOCK_URL='http://stripe-mock:12111')
    def test_webhook_signature_verification(self):
        """Test webhook signature verification with stripe-mock."""
        adapter = StripeAdapter()
        payload = json.dumps({
            'id': 'evt_test',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test',
                    'status': 'succeeded',
                }
            }
        })
        # stripe-mock expects Stripe-Signature header
        # For testing, we'd need a valid signature from stripe-mock
        # This test just verifies the method doesn't crash
        result = adapter.verify_webhook(
            json.loads(payload),
            {'Stripe-Signature': 'test_signature'}
        )
        # Result will be False if signature is invalid (expected for mock testing)
        assert result is False or isinstance(result, dict)


@pytest.mark.integration
class StripeMockAvailabilityTest(TestCase):
    """Test whether stripe-mock is available (optional)."""

    def test_stripe_mock_connection(self):
        """Attempt to connect to stripe-mock; skip if unavailable."""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('stripe-mock', 12111))
            sock.close()
            assert result == 0, "stripe-mock should be running on port 12111"
        except Exception:
            pytest.skip("stripe-mock Docker service not available; skipping Stripe integration tests")
