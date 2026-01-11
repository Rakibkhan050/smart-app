import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

@pytest.mark.django_db
def test_webhook_ok():
    client = APIClient()
    # Use the test webhook endpoint which bypasses signature checks (requires auth)
    User = get_user_model()
    u = User.objects.create_user('tester', 'tester@example.com', 'pass')
    client.force_authenticate(u)
    resp = client.post(reverse('test_webhook'), {'payment_id': 'p1', 'amount': 10}, format='json')
    assert resp.status_code == 200
    assert resp.data['status'] == 'ok'