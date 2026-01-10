import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest import mock

User = get_user_model()

@pytest.mark.django_db
def test_test_webhook_enqueues_task(monkeypatch):
    user = User.objects.create_user(username='tester', password='p')
    client = APIClient()
    client.force_authenticate(user=user)

    called = {}

    def fake_delay(**kwargs):
        called['called'] = True
        called['kwargs'] = kwargs

    monkeypatch.setattr('receipts.tasks.generate_receipt_for_payment.delay', fake_delay)

    resp = client.post(reverse('payment_webhook'), {'payment_id': 'p1', 'amount': 100, 'currency': 'SAR'}, format='json', HTTP_X_PAYMENT_PROVIDER='paytabs', HTTP_X_PAYMENT_SIGNATURE='dummy')
    # Since verify will use secret and HMAC, signature won't validate; expect 403
    assert resp.status_code == 403

    # Call test-webhook endpoint which bypasses signature checks
    resp2 = client.post(reverse('test_webhook'), {'payment_id': 'p_test', 'amount': 50}, format='json')
    assert resp2.status_code == 200
    assert called.get('called', False) is True
