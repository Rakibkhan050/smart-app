import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_webhook_ok():
    client = APIClient()
    resp = client.post(reverse('payment_webhook'), {'foo': 'bar'}, format='json')
    assert resp.status_code == 200
    assert resp.data['status'] == 'ok'
