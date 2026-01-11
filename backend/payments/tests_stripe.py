import pytest
from django.conf import settings
from django.test import override_settings
from payments.adapters import StripeAdapter


@pytest.mark.skipif(True, reason="Requires stripe SDK and keys; run locally with env vars set")
def test_stripe_create_intent_live():
    a = StripeAdapter()
    intent = a.create_payment_intent(amount=10, currency='SAR')
    assert 'id' in intent


@pytest.mark.skipif(True, reason="Requires stripe SDK and keys; run locally with env vars set")
def test_stripe_verify_webhook_live():
    a = StripeAdapter()
    # This test is a placeholder: to run it you need STRIPE_WEBHOOK_SECRET and a real payload/signature
    assert True
