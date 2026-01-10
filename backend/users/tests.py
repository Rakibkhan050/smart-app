import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_register_and_token():
    client = APIClient()
    data = {'username': 'jdoe', 'email': 'jdoe@example.com', 'password': 'pass1234'}
    resp = client.post(reverse('register'), data)
    assert resp.status_code == 201

    # obtain token
    token_resp = client.post(reverse('token_obtain_pair'), {'username': 'jdoe', 'password': 'pass1234'})
    assert token_resp.status_code == 200
    assert 'access' in token_resp.data
