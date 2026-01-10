import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_presign_requires_filename():
    user = User.objects.create_user(username='u', password='p')
    client = APIClient()
    client.force_authenticate(user=user)
    resp = client.post(reverse('receipts-presign-upload'))
    assert resp.status_code == 400
