import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_subscribe_flow():
    user = User.objects.create_user(username='bob', password='pass')
    client = APIClient()
    client.force_authenticate(user=user)
    data = {'endpoint': 'https://example.com/push/abc', 'keys': {'p256dh': 'abc', 'auth': 'def'}}
    resp = client.post(reverse('notifications-subscribe'), data, format='json')
    assert resp.status_code == 200
    assert resp.data['status'] == 'subscribed'
