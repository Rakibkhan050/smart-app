import pytest
from django.test import override_settings
from django.urls import reverse
from django.test import Client


@pytest.mark.skipif(True, reason="Integration test: requires STRIPE_WEBHOOK_SECRET and stripe payload")
def test_stripe_webhook_integration():
    c = Client()
    # This is a placeholder to be executed manually with a signed Stripe payload
    resp = c.post(reverse('payment_webhook'), data={'id': 'pi_test'}, content_type='application/json', HTTP_X_PAYMENT_PROVIDER='stripe')
    assert resp.status_code in (200, 201)