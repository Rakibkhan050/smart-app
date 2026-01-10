import pytest
from django.contrib.auth import get_user_model
from .models import Notification
from .serializers import NotificationSerializer

User = get_user_model()

@pytest.mark.django_db
def test_notification_serializer():
    user = User.objects.create_user(username='testuser', password='pass')
    n = Notification.objects.create(recipient=user, title='Hello', body='Test')
    s = NotificationSerializer(n)
    data = s.data
    assert data['title'] == 'Hello'
    assert data['recipient'] == user.id
